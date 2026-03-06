"""
Target runner - start/stop target apps as subprocesses.

- Start Flask app on chosen localhost port
- wait_for_health(url, timeout)
- Stop process cleanly
- Capture stdout/stderr to run folder
"""

import os
import subprocess
import sys
from pathlib import Path

import httpx

from config.schema import TargetRunConfig


def start_target(
    target_config: TargetRunConfig,
    run_folder: Path,
    project_root: Path,
) -> subprocess.Popen:
    """
    Start target app as subprocess. Captures stdout/stderr to run folder.

    Returns:
        Popen instance. Call stop_target() or process.terminate() to stop.
    """
    app_path = project_root / target_config.path
    if not app_path.exists():
        raise FileNotFoundError(f"Target app not found: {app_path}")

    env = {"PORT": str(target_config.port), "FLASK_APP": str(app_path)}
    stdout_file = run_folder / "target_stdout.log"
    stderr_file = run_folder / "target_stderr.log"

    with open(stdout_file, "w") as out, open(stderr_file, "w") as err:
        proc = subprocess.Popen(
            [sys.executable, str(app_path)],
            cwd=str(project_root),
            env={**os.environ, **env},
            stdout=out,
            stderr=err,
        )
    return proc


def wait_for_health(base_url: str, timeout: float = 30.0, poll_interval: float = 0.2) -> bool:
    """Poll until /health returns 200 or timeout."""
    import time
    url = f"{base_url.rstrip('/')}/health"
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            r = httpx.get(url, timeout=2.0)
            if r.status_code == 200:
                return True
        except Exception:
            pass
        time.sleep(poll_interval)
    return False


def stop_target(proc: subprocess.Popen, timeout: float = 5.0) -> None:
    """Terminate target process cleanly."""
    try:
        proc.terminate()
        proc.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()
