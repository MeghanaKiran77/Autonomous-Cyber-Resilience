"""Pytest fixtures."""

import os
import subprocess
import sys
import time
from pathlib import Path

import httpx
import pytest


@pytest.fixture(scope="module")
def flask_app_port():
    """Use port 5099 for tests to avoid clashes."""
    return 5099


@pytest.fixture(scope="module")
def flask_app(flask_app_port, tmp_path_factory):
    """Start Flask app, yield base_url, stop on teardown."""
    project_root = Path(__file__).resolve().parent.parent
    app_path = project_root / "targets" / "flask_sqli_demo" / "app.py"
    if not app_path.exists():
        pytest.skip("Flask app not found")
    env = {**os.environ, "PORT": str(flask_app_port)}
    out = tmp_path_factory.mktemp("logs") / "out.log"
    err = tmp_path_factory.mktemp("logs") / "err.log"
    with open(out, "w") as fo, open(err, "w") as fe:
        proc = subprocess.Popen(
            [sys.executable, str(app_path)],
            cwd=str(project_root),
            env=env,
            stdout=fo,
            stderr=fe,
        )
    base_url = f"http://127.0.0.1:{flask_app_port}"
    for _ in range(50):
        try:
            r = httpx.get(f"{base_url}/health", timeout=1.0)
            if r.status_code == 200:
                break
        except Exception:
            time.sleep(0.1)
    else:
        proc.terminate()
        proc.wait()
        pytest.fail("Flask app did not become healthy")
    yield base_url
    proc.terminate()
    proc.wait(timeout=5)
