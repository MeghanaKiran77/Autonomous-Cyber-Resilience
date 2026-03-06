"""Smoke tests: health works, exploit triggers leak marker, oracle detects it."""

from urllib.parse import quote

import httpx
import pytest

from config.schema import OracleConfig
from oracle.verification import verify_exploit


def test_health_works(flask_app):
    """Health endpoint returns 200 OK."""
    r = httpx.get(f"{flask_app}/health", timeout=5.0)
    assert r.status_code == 200
    assert "OK" in r.text


def test_exploit_triggers_leak_marker(flask_app):
    """SQLi payload returns response containing LEAK_MARKER."""
    payload = "' OR '1'='1"
    r = httpx.get(f"{flask_app}/search?q={quote(payload)}", timeout=5.0)
    assert r.status_code == 200
    assert "LEAK_MARKER" in r.text


def test_oracle_detects_exploit(flask_app):
    """Oracle correctly identifies exploit success when LEAK_MARKER present."""
    payload = "' OR '1'='1"
    r = httpx.get(f"{flask_app}/search?q={quote(payload)}", timeout=5.0)
    oracle_config = OracleConfig(success_contains_any=["LEAK_MARKER"])
    verdict, evidence = verify_exploit(
        status_code=r.status_code,
        response_text=r.text,
        oracle_config=oracle_config,
    )
    assert verdict["exploit_success"] is True
    assert verdict["status_code"] == 200
    assert "reason" in verdict
    assert "LEAK_MARKER" in evidence["matched_markers"]
    assert "snippet" in evidence
    assert evidence["snippet"]
