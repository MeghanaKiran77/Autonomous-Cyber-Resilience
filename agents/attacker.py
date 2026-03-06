"""
Attacker Agent - Generates Proof-of-Concept exploits.

Responsibilities:
- Consume Researcher findings
- Generate PoC exploits for SQLi, IDOR, XSS
- Output exploits in a format the Oracle can verify
- Use fast, creative models (llama-4-scout or llama-3.3-70b)
"""

import json
from pathlib import Path
from typing import Any

import structlog

from config.agent_models import get_agent_model
from config.schema import LLMConfig
from llm.factory import create_llm_client

log = structlog.get_logger()


# Attacker Agent prompt templates
SYSTEM_PROMPT = """You are an ethical penetration tester generating Proof-of-Concept (PoC) exploits for security research.

Your task is to create precise, testable exploit payloads based on vulnerability findings.

For each finding, generate:
1. The HTTP method (GET, POST, etc.)
2. The full endpoint URL
3. The exploit payload
4. Expected success markers (what indicates the exploit worked)

IMPORTANT:
- Generate ONLY exploits for confirmed vulnerabilities
- Payloads must be precise and testable
- Include clear success criteria
- This is for authorized security research only

SQL INJECTION EXPERTISE:
When generating SQLi payloads, consider common query patterns:
- LIKE queries: Use `%' OR '1'='1' --` or `%' UNION SELECT ...`
- WHERE clauses: Use `' OR '1'='1' --` or `' UNION SELECT ...`
- String concatenation: Escape quotes properly
- Always try to close existing quotes/parentheses first
- Use `--` or `#` to comment out remaining query

Common SQLi payloads by pattern:
1. LIKE '%input%': Try `%' OR '1'='1' --` or just `%` to match all
2. WHERE col='input': Try `' OR '1'='1' --`
3. WHERE col=input: Try `1 OR 1=1 --`

Be creative but precise. The exploits will be tested against sandboxed targets."""


def generate_exploits(
    findings: dict[str, Any],
    target_spec: dict[str, Any],
    run_folder: Path,
    max_attempts: int = 3,
) -> list[dict[str, Any]]:
    """
    Generate PoC exploits from Researcher findings.

    Args:
        findings: Structured findings from Researcher Agent.
        target_spec: Target specification (type, port, etc.).
        run_folder: Path to run folder for artifacts.
        max_attempts: Maximum refinement attempts per exploit (default: 3).

    Returns:
        List of exploit payloads.
    """
    log.info(
        "attacker_generating",
        finding_count=len(findings.get("findings", [])),
        target_type=target_spec.get("type"),
    )

    if not findings.get("findings"):
        log.warning("attacker_no_findings")
        return []

    # Get optimal model for Attacker (llama-4-scout or fallback)
    try:
        agent_config = get_agent_model("attacker")
    except Exception:
        # Fallback if llama-4-scout not available
        from config.agent_models import AgentModelConfig
        agent_config = AgentModelConfig(
            provider="groq",
            model="llama-3.3-70b-versatile",
            temperature=0.5,
            max_tokens=1024,
            reasoning="Fallback model for exploit generation"
        )
    
    # Create LLM client
    llm_config = LLMConfig(provider=agent_config.provider, model=agent_config.model)
    client = create_llm_client(llm_config)

    # Build exploit generation prompt
    prompt = _build_exploit_prompt(findings, target_spec)
    
    # Define expected output schema
    schema = {
        "exploits": [
            {
                "finding_id": "number",
                "method": "GET | POST",
                "endpoint": "string",
                "payload": "string",
                "expected_marker": "string",
                "description": "string",
            }
        ]
    }

    try:
        # Call LLM with structured output
        result = client.call_structured(
            prompt=prompt,
            schema=schema,
            system=SYSTEM_PROMPT,
            temperature=agent_config.temperature,
        )

        exploits = result.get("exploits", [])

        # Write exploits to run folder
        exploits_path = run_folder / "exploits.json"
        exploits_path.write_text(json.dumps(result, indent=2))

        log.info(
            "attacker_complete",
            exploit_count=len(exploits),
            exploits_path=str(exploits_path),
        )

        return exploits

    except Exception as e:
        log.error("attacker_failed", error=str(e))
        return []


def refine_exploit(
    original_exploit: dict[str, Any],
    failure_reason: str,
    response_body: str,
    target_spec: dict[str, Any],
    attempt: int,
) -> dict[str, Any] | None:
    """
    Refine a failed exploit based on Oracle feedback.

    Args:
        original_exploit: The exploit that failed.
        failure_reason: Why the exploit failed (from Oracle).
        response_body: The actual response received.
        target_spec: Target specification.
        attempt: Current attempt number.

    Returns:
        Refined exploit or None if refinement fails.
    """
    log.info(
        "attacker_refining",
        attempt=attempt,
        original_payload=original_exploit.get("payload"),
        failure_reason=failure_reason,
    )

    # Get model config
    try:
        agent_config = get_agent_model("attacker")
    except Exception:
        from config.agent_models import AgentModelConfig
        agent_config = AgentModelConfig(
            provider="groq",
            model="llama-3.3-70b-versatile",
            temperature=0.5,
            max_tokens=1024,
            reasoning="Fallback model"
        )
    
    # Create LLM client
    llm_config = LLMConfig(provider=agent_config.provider, model=agent_config.model)
    client = create_llm_client(llm_config)

    # Build refinement prompt
    prompt = _build_refinement_prompt(
        original_exploit, failure_reason, response_body, target_spec, attempt
    )
    
    # Define schema for refined exploit
    schema = {
        "refined_payload": "string",
        "reasoning": "string",
        "expected_marker": "string",
    }

    try:
        result = client.call_structured(
            prompt=prompt,
            schema=schema,
            system=SYSTEM_PROMPT,
            temperature=agent_config.temperature + 0.1,  # Slightly higher for creativity
        )

        # Create refined exploit
        refined = original_exploit.copy()
        refined["payload"] = result.get("refined_payload", "")
        refined["expected_marker"] = result.get("expected_marker", refined.get("expected_marker"))
        refined["description"] = f"Attempt {attempt}: {result.get('reasoning', '')}"

        log.info(
            "attacker_refined",
            attempt=attempt,
            new_payload=refined["payload"],
        )

        return refined

    except Exception as e:
        log.error("attacker_refinement_failed", attempt=attempt, error=str(e))
        return None


def _build_exploit_prompt(findings: dict, target_spec: dict) -> str:
    """Build exploit generation prompt from findings."""
    
    base_url = f"http://127.0.0.1:{target_spec.get('port', 5000)}"
    
    prompt = f"""Generate Proof-of-Concept exploits for these vulnerability findings:

TARGET:
- Base URL: {base_url}
- Type: {target_spec.get('type', 'unknown')}

FINDINGS:
"""
    
    for i, finding in enumerate(findings.get("findings", []), 1):
        prompt += f"\nFinding {i}:\n"
        prompt += f"  Endpoint: {finding.get('endpoint')}\n"
        prompt += f"  Parameter: {finding.get('parameter')}\n"
        prompt += f"  Type: {finding.get('vulnerability_type')}\n"
        prompt += f"  Confidence: {finding.get('confidence')}\n"
        prompt += f"  Reasoning: {finding.get('reasoning', '')[:200]}\n"

    prompt += """

TASK:
For each finding with confidence >= 0.5, generate a PoC exploit:

1. finding_id: The finding number (1, 2, 3, etc.)
2. method: HTTP method (GET or POST)
3. endpoint: Full endpoint path (e.g., "/search")
4. payload: The exploit payload (e.g., "' OR '1'='1" for SQLi)
5. expected_marker: What indicates success (e.g., "LEAK_MARKER" for SQLi)
6. description: Brief description of what the exploit does

Focus on exploits that are:
- Precise and testable
- Likely to succeed based on the findings
- Safe for sandboxed testing

For SQLi, consider that the query might use LIKE patterns. Try payloads like:
- `%' OR '1'='1' --` (for LIKE queries)
- `%` (to match all rows in LIKE)
- `' OR '1'='1' --` (for standard WHERE)"""

    return prompt


def _build_refinement_prompt(
    original_exploit: dict,
    failure_reason: str,
    response_body: str,
    target_spec: dict,
    attempt: int,
) -> str:
    """Build refinement prompt based on failure feedback."""
    
    prompt = f"""EXPLOIT REFINEMENT - Attempt {attempt}

ORIGINAL EXPLOIT:
- Endpoint: {original_exploit.get('endpoint')}
- Method: {original_exploit.get('method')}
- Payload: {original_exploit.get('payload')}
- Expected: {original_exploit.get('expected_marker')}

FAILURE ANALYSIS:
- Reason: {failure_reason}
- Response: {response_body[:300]}

TARGET INFO:
- Type: {target_spec.get('type', 'unknown')}
- Port: {target_spec.get('port', 5000)}

TASK:
The original exploit failed. Analyze why and generate a refined payload.

Common SQLi failure patterns:
1. Syntax error: Quote/parenthesis mismatch - try different escape sequences
2. Empty results: Payload didn't match query pattern - try LIKE-specific payloads
3. No LEAK_MARKER: Payload didn't return sensitive data - try UNION or broader match

For LIKE queries specifically:
- Pattern: `WHERE col LIKE '%input%'`
- Working payloads: `%' OR '1'='1' --`, `%' UNION SELECT ...`, or just `%`
- The `%` wildcard matches everything in LIKE

Generate a refined payload that:
1. Addresses the failure reason
2. Uses a different technique than the original
3. Is more likely to succeed

Return:
- refined_payload: The new payload to try
- reasoning: Why this should work better
- expected_marker: What indicates success (usually "LEAK_MARKER" for SQLi)"""

    return prompt
