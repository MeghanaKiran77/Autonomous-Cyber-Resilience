"""
Verification Oracle - Config-driven rule engine for exploit verification.

Accepts status_code, response_text, optional headers/body metadata,
and oracle config from RunConfig (pydantic validated).
"""

from typing import Any

import structlog

from config.schema import OracleConfig

log = structlog.get_logger()


def verify_exploit(
    status_code: int,
    response_text: str,
    oracle_config: OracleConfig,
    headers: dict[str, str] | None = None,
    body_metadata: dict[str, Any] | None = None,
) -> tuple[dict, dict]:
    """
    Verify exploit success using config-driven rules.

    Args:
        status_code: HTTP status code.
        response_text: Response body text.
        oracle_config: Oracle rules from RunConfig.
        headers: Optional response headers.
        body_metadata: Optional body metadata (e.g., parsed JSON keys).

    Returns:
        (verdict, evidence) where:
        verdict: {exploit_success: bool, reason: str, status_code: int}
        evidence: {matched_markers: list[str], snippet: str}
    """
    max_len = oracle_config.max_snippet_len
    snippet = response_text[:max_len] if response_text else ""
    matched_markers: list[str] = []
    reason_parts: list[str] = []

    # Status code rules
    if status_code in oracle_config.fail_status_codes:
        reason_parts.append(f"status {status_code} in fail_status_codes")
        verdict = {
            "exploit_success": False,
            "reason": "; ".join(reason_parts),
            "status_code": status_code,
        }
        evidence = {"matched_markers": [], "snippet": snippet}
        log.info("oracle_verdict", exploit_success=False, reason=reason_parts[0])
        return verdict, evidence

    if status_code not in oracle_config.success_status_codes and oracle_config.success_status_codes:
        reason_parts.append(f"status {status_code} not in success_status_codes {oracle_config.success_status_codes}")

    # fail_contains_any: if any present -> fail
    if oracle_config.fail_contains_any:
        for m in oracle_config.fail_contains_any:
            if m in response_text:
                reason_parts.append(f"response contains fail marker: {m!r}")
                verdict = {
                    "exploit_success": False,
                    "reason": "; ".join(reason_parts),
                    "status_code": status_code,
                }
                evidence = {"matched_markers": [], "snippet": snippet}
                log.info("oracle_verdict", exploit_success=False, reason=reason_parts[-1])
                return verdict, evidence

    # success_contains_all: must match all
    if oracle_config.success_contains_all:
        for m in oracle_config.success_contains_all:
            if m in response_text:
                matched_markers.append(m)
            else:
                reason_parts.append(f"missing success_contains_all: {m!r}")
                verdict = {
                    "exploit_success": False,
                    "reason": "; ".join(reason_parts),
                    "status_code": status_code,
                }
                evidence = {"matched_markers": matched_markers, "snippet": snippet}
                log.info("oracle_verdict", exploit_success=False, reason=reason_parts[-1])
                return verdict, evidence

    # success_contains_any: at least one match -> success (if status was ok)
    if oracle_config.success_contains_any:
        for m in oracle_config.success_contains_any:
            if m in response_text:
                matched_markers.append(m)
        if not matched_markers:
            reason_parts.append(
                f"no success_contains_any match in {oracle_config.success_contains_any}"
            )

    # Final verdict: success iff status ok, no fail triggers, and success rules satisfied
    exploit_success = (
        status_code in oracle_config.success_status_codes
        and not any("fail" in r for r in reason_parts)
        and (bool(matched_markers) or not oracle_config.success_contains_any)
        and (
            oracle_config.success_contains_all is None
            or len(matched_markers) >= len(oracle_config.success_contains_all)
        )
    )
    if not reason_parts:
        reason_parts.append("ok")

    verdict = {
        "exploit_success": exploit_success,
        "reason": "; ".join(reason_parts),
        "status_code": status_code,
    }
    evidence = {"matched_markers": matched_markers, "snippet": snippet}
    log.info("oracle_verdict", exploit_success=exploit_success, matched=matched_markers)
    return verdict, evidence


def verify_patch(exploit: dict, patch: dict, target: dict) -> dict:
    """
    Verify that a patch suppresses the exploit and introduces no regression.

    TODO: udocker integration; rule-based regression checks.
    """
    log.info("oracle_verifying_patch", target_type=target.get("type", "unknown"))
    return {"suppressed": False, "regression": False, "evidence": None}
