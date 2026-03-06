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


def verify_patch(
    exploit: dict[str, Any],
    patch: dict[str, Any],
    patched_target_url: str,
    oracle_config: OracleConfig,
) -> dict[str, Any]:
    """
    Verify that a patch suppresses the exploit and introduces no regression.

    Args:
        exploit: Original exploit that succeeded.
        patch: Generated patch information.
        patched_target_url: Base URL of patched target.
        oracle_config: Oracle rules for verification.

    Returns:
        dict with:
        - suppressed: bool (exploit now fails)
        - regression: bool (benign requests still work)
        - evidence: dict with test results
    """
    import httpx
    from urllib.parse import quote
    
    log.info("oracle_verifying_patch", target_url=patched_target_url)
    
    evidence = {
        "exploit_test": {},
        "benign_tests": [],
    }
    
    # Test 1: Verify exploit is suppressed
    try:
        endpoint = exploit.get("endpoint", "")
        payload = exploit.get("payload", "")
        method = exploit.get("method", "GET")
        
        if method == "GET":
            # Try the original exploit against patched target
            exploit_url = f"{patched_target_url}{endpoint}?q={quote(payload)}"
            
            log.info("oracle_testing_exploit_suppression", url=exploit_url)
            r = httpx.get(exploit_url, timeout=5.0)
            
            # Verify exploit using same rules
            verdict, _ = verify_exploit(
                status_code=r.status_code,
                response_text=r.text,
                oracle_config=oracle_config,
            )
            
            exploit_suppressed = not verdict.get("exploit_success", False)
            
            evidence["exploit_test"] = {
                "url": exploit_url,
                "status": r.status_code,
                "suppressed": exploit_suppressed,
                "response_snippet": r.text[:200],
            }
            
            log.info(
                "oracle_exploit_suppression_result",
                suppressed=exploit_suppressed,
                status=r.status_code,
            )
            
    except Exception as e:
        log.error("oracle_exploit_test_failed", error=str(e))
        exploit_suppressed = False
        evidence["exploit_test"] = {"error": str(e)}
    
    # Test 2: Verify no regression with benign requests
    benign_tests = [
        {"name": "empty_search", "query": ""},
        {"name": "simple_search", "query": "apple"},
        {"name": "special_chars", "query": "test@123"},
    ]
    
    regression_detected = False
    
    for test in benign_tests:
        try:
            test_url = f"{patched_target_url}{endpoint}?q={quote(test['query'])}"
            
            log.info("oracle_testing_benign", test_name=test["name"], url=test_url)
            r = httpx.get(test_url, timeout=5.0)
            
            # Benign requests should return 200 and not contain LEAK_MARKER
            test_passed = (
                r.status_code == 200
                and "LEAK_MARKER" not in r.text
            )
            
            if not test_passed:
                regression_detected = True
            
            evidence["benign_tests"].append({
                "name": test["name"],
                "query": test["query"],
                "status": r.status_code,
                "passed": test_passed,
                "response_snippet": r.text[:200],
            })
            
            log.info(
                "oracle_benign_test_result",
                test_name=test["name"],
                passed=test_passed,
            )
            
        except Exception as e:
            log.error("oracle_benign_test_failed", test_name=test["name"], error=str(e))
            regression_detected = True
            evidence["benign_tests"].append({
                "name": test["name"],
                "error": str(e),
                "passed": False,
            })
    
    # Final verdict
    result = {
        "suppressed": exploit_suppressed,
        "regression": regression_detected,
        "evidence": evidence,
        "patch_effective": exploit_suppressed and not regression_detected,
    }
    
    log.info(
        "oracle_patch_verification_complete",
        suppressed=exploit_suppressed,
        regression=regression_detected,
        effective=result["patch_effective"],
    )
    
    return result
