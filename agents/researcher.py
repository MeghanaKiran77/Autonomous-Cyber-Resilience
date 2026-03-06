"""
Researcher Agent - Dynamically analyzes vulnerable application-layer targets.

Responsibilities:
- Analyze target applications for SQLi, IDOR, XSS vulnerabilities
- Produce structured findings for the Attacker Agent
- Use deep reasoning models (qwen-qwq-32b) for thorough analysis
"""

import json
from pathlib import Path
from typing import Any

import structlog

from config.agent_models import get_agent_model
from config.schema import LLMConfig
from llm.factory import create_llm_client

log = structlog.get_logger()


# Researcher Agent prompt templates
SYSTEM_PROMPT = """You are a security researcher specializing in application-layer vulnerability analysis.

Your task is to analyze web applications for common vulnerabilities:
- SQL Injection (SQLi)
- Insecure Direct Object Reference (IDOR)
- Cross-Site Scripting (XSS)

You must:
1. Analyze the target specification and reconnaissance data
2. Identify potential vulnerability points (endpoints, parameters)
3. Assess confidence level (0.0-1.0) for each finding
4. Provide clear reasoning for each vulnerability hypothesis

Be thorough and methodical. Use your reasoning capabilities to find obscure logic flaws."""


def analyze_target(
    target_spec: dict[str, Any],
    recon_data: dict[str, Any],
    run_folder: Path,
) -> dict[str, Any]:
    """
    Analyze target and produce findings for the Attacker Agent.

    Args:
        target_spec: Target specification (type, path, port, etc.).
        recon_data: Reconnaissance data from initial probes.
        run_folder: Path to run folder for artifacts.

    Returns:
        Structured findings dict with vulnerability hypotheses.
    """
    log.info(
        "researcher_analyzing",
        target_type=target_spec.get("type"),
        target_name=target_spec.get("name"),
    )

    # Get optimal model for Researcher (qwen-qwq-32b)
    agent_config = get_agent_model("researcher")
    
    # Create LLM client
    llm_config = LLMConfig(provider=agent_config.provider, model=agent_config.model)
    client = create_llm_client(llm_config)

    # Build analysis prompt
    prompt = _build_analysis_prompt(target_spec, recon_data)
    
    # Define expected output schema
    schema = {
        "findings": [
            {
                "endpoint": "string",
                "parameter": "string",
                "vulnerability_type": "sqli | idor | xss",
                "confidence": "number (0.0-1.0)",
                "reasoning": "string",
            }
        ]
    }

    try:
        # Call LLM with structured output
        findings = client.call_structured(
            prompt=prompt,
            schema=schema,
            system=SYSTEM_PROMPT,
            temperature=agent_config.temperature,
        )

        # Write findings to run folder
        findings_path = run_folder / "findings.json"
        findings_path.write_text(json.dumps(findings, indent=2))

        log.info(
            "researcher_complete",
            finding_count=len(findings.get("findings", [])),
            findings_path=str(findings_path),
        )

        return findings

    except Exception as e:
        log.error("researcher_failed", error=str(e))
        # Return empty findings on failure
        return {"findings": [], "error": str(e)}


def _build_analysis_prompt(target_spec: dict, recon_data: dict) -> str:
    """Build analysis prompt from target spec and recon data."""
    
    prompt = f"""Analyze this web application for vulnerabilities:

TARGET SPECIFICATION:
- Type: {target_spec.get('type', 'unknown')}
- Name: {target_spec.get('name', 'unknown')}
- Base URL: http://127.0.0.1:{target_spec.get('port', 5000)}

RECONNAISSANCE DATA:
"""
    
    # Add recon data for each endpoint
    for endpoint, data in recon_data.items():
        prompt += f"\nEndpoint: {endpoint}\n"
        if "error" in data:
            prompt += f"  Error: {data['error']}\n"
        else:
            prompt += f"  Status: {data.get('status', 'unknown')}\n"
            body_preview = data.get('body_preview', '')[:200]
            prompt += f"  Response preview: {body_preview}\n"

    prompt += """

TASK:
Identify potential vulnerabilities in this application. For each finding, provide:
1. The vulnerable endpoint
2. The vulnerable parameter (if applicable)
3. The vulnerability type (sqli, idor, or xss)
4. Your confidence level (0.0 to 1.0)
5. Your reasoning

Focus on the most likely vulnerabilities based on the reconnaissance data."""

    return prompt
