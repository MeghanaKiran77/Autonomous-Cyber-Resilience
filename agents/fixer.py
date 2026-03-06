"""
Fixer Agent - Generates patches for verified vulnerabilities.

Responsibilities:
- Consume verified exploit + target context
- Generate patches that suppress exploit
- Preserve regression-free functionality
- Use code-focused models (gpt-oss-120b or fallback)
"""

import json
from pathlib import Path
from typing import Any

import structlog

from config.agent_models import get_agent_model
from config.schema import LLMConfig
from llm.factory import create_llm_client

log = structlog.get_logger()


# Fixer Agent prompt templates
SYSTEM_PROMPT = """You are a security engineer specializing in vulnerability remediation.

Your task is to generate secure patches that fix verified vulnerabilities while preserving functionality.

For each vulnerability, provide:
1. Root cause analysis
2. Secure code fix (complete patched code)
3. Explanation of why the fix works
4. Regression prevention notes

SECURITY BEST PRACTICES:

SQL Injection Fixes:
- Use parameterized queries (prepared statements)
- NEVER concatenate user input into SQL
- Use ORM query builders when possible
- Validate and sanitize input as defense-in-depth
- Example (Python/SQLite):
  ```python
  # BAD: cur.execute(f"SELECT * FROM items WHERE name LIKE '%{q}%'")
  # GOOD: cur.execute("SELECT * FROM items WHERE name LIKE ?", (f"%{q}%",))
  ```

IDOR Fixes:
- Implement proper authorization checks
- Verify user owns the resource before access
- Use session-based access control
- Never trust client-provided IDs without verification

XSS Fixes:
- Escape all user input in HTML context
- Use framework auto-escaping (Jinja2, React, etc.)
- Set Content-Security-Policy headers
- Sanitize input on server side

IMPORTANT:
- Preserve all existing functionality
- Maintain code style and structure
- Add comments explaining the security fix
- Ensure the patch is minimal and focused"""


def generate_patch(
    exploit: dict[str, Any],
    target_spec: dict[str, Any],
    target_source: str,
    run_folder: Path,
) -> dict[str, Any]:
    """
    Generate patch for a verified vulnerability.

    Args:
        exploit: Verified exploit payload.
        target_spec: Target application spec.
        target_source: Source code of vulnerable target.
        run_folder: Path to run folder for artifacts.

    Returns:
        Patch specification with patched code.
    """
    log.info(
        "fixer_generating",
        target_type=target_spec.get("type"),
        endpoint=exploit.get("endpoint"),
    )

    # Get optimal model for Fixer (gpt-oss-120b or fallback)
    try:
        agent_config = get_agent_model("fixer")
    except Exception:
        # Fallback if gpt-oss-120b not available
        from config.agent_models import AgentModelConfig
        agent_config = AgentModelConfig(
            provider="groq",
            model="llama-3.3-70b-versatile",
            temperature=0.2,
            max_tokens=2048,
            reasoning="Fallback model for patch generation"
        )
    
    # Create LLM client
    llm_config = LLMConfig(provider=agent_config.provider, model=agent_config.model)
    client = create_llm_client(llm_config)

    # Build patch generation prompt
    prompt = _build_patch_prompt(exploit, target_spec, target_source)
    
    # Define expected output schema
    schema = {
        "root_cause": "string - brief explanation of the vulnerability",
        "patch_description": "string - description of the fix",
        "explanation": "string - why this fix prevents the exploit",
        "regression_notes": "string - what to test",
    }

    try:
        # Call LLM with structured output (without code in JSON)
        result = client.call_structured(
            prompt=prompt,
            schema=schema,
            system=SYSTEM_PROMPT,
            temperature=agent_config.temperature,
        )

        # Now get the patched code separately (as plain text)
        code_prompt = f"""Based on this vulnerability fix:

Root Cause: {result.get('root_cause', '')}
Fix Description: {result.get('patch_description', '')}

Generate the complete patched source code for:
{target_source}

Provide ONLY the patched Python code, no explanations, no markdown, no JSON."""

        code_response = client.call(
            prompt=code_prompt,
            system="You are a code generator. Output only valid Python code, no markdown, no explanations.",
            temperature=0.1,  # Very low for deterministic code
            max_tokens=2048,
        )

        # Clean up code response (remove markdown if present)
        patched_code = code_response.content.strip()
        if patched_code.startswith("```"):
            lines = patched_code.split("\n")
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            patched_code = "\n".join(lines)

        # Add patched code to result
        result["patched_code"] = patched_code

        # Write patch to run folder
        patch_path = run_folder / "patch.json"
        patch_path.write_text(json.dumps(result, indent=2))

        # Also write just the patched code for easy application
        patched_code_path = run_folder / "patched_code.py"
        patched_code_path.write_text(patched_code)

        log.info(
            "fixer_complete",
            patch_path=str(patch_path),
            root_cause=result.get("root_cause", "")[:100],
        )

        return result

    except Exception as e:
        log.error("fixer_failed", error=str(e))
        return {
            "root_cause": "Error generating patch",
            "patched_code": "",
            "patch_description": "",
            "explanation": str(e),
            "regression_notes": "",
        }


def _build_patch_prompt(
    exploit: dict,
    target_spec: dict,
    target_source: str,
) -> str:
    """Build patch generation prompt from exploit and target source."""
    
    vuln_type = target_spec.get("type", "unknown")
    
    prompt = f"""Generate a secure patch for this verified vulnerability:

VULNERABILITY TYPE: {vuln_type.upper()}

VERIFIED EXPLOIT:
- Endpoint: {exploit.get('endpoint')}
- Method: {exploit.get('method')}
- Payload: {exploit.get('payload')}
- Description: {exploit.get('description', '')}

VULNERABLE SOURCE CODE:
```python
{target_source}
```

TASK:
Analyze the vulnerability and describe the fix (code will be generated separately).

Provide:
1. root_cause: Brief explanation of why the vulnerability exists
2. patch_description: Detailed description of how to fix it (use parameterized queries, etc.)
3. explanation: Why this fix prevents the exploit
4. regression_notes: What to test to ensure no functionality is broken

REQUIREMENTS:
- For SQL injection: Use parameterized queries (prepared statements)
- Preserve all existing functionality
- Ensure the patch is production-ready

Focus on describing the fix clearly and completely."""

    return prompt
