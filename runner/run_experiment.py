"""
Single entrypoint for experiment execution.

Usage:
    python -m runner.run_experiment --config configs/run.yaml
"""

import sys

if sys.version_info < (3, 11):
    print("Error: This project requires Python 3.11+.", file=sys.stderr)
    print(f"Current: {sys.version}", file=sys.stderr)
    print("Run: pyenv shell 3.11", file=sys.stderr)
    sys.exit(1)

import json
from pathlib import Path
from urllib.parse import quote

import click
import httpx
import structlog

from config.loader import load_config
from config.schema import RunConfig
from oracle.verification import verify_exploit
from targets.runner import start_target, stop_target, wait_for_health
from utils.logging_config import setup_logging
from utils.run_folder import create_run_folder, get_run_id


def _run_minimal_pipeline(
    config: RunConfig, run_folder: Path, project_root: Path, log: structlog.BoundLogger
) -> None:
    """Minimal non-LLM pipeline: start target, recon, exploit, oracle, stop."""
    tr = config.target_run
    if not tr:
        log.info("skipping_minimal_pipeline", reason="target_run not configured")
        return

    base_url = f"http://127.0.0.1:{tr.port}"

    proc = start_target(tr, run_folder, project_root)
    try:
        if not wait_for_health(base_url, timeout=30.0):
            log.error("target_health_failed", url=base_url)
            return

        # Recon
        recon = {}
        for path in ["/", "/health", "/search?q=test"]:
            try:
                r = httpx.get(f"{base_url}{path}", timeout=5.0)
                recon[path] = {"status": r.status_code, "body_preview": r.text[:500]}
            except Exception as e:
                recon[path] = {"error": str(e)}
        (run_folder / "recon.json").write_text(json.dumps(recon, indent=2))
        log.info("recon_complete", paths=list(recon.keys()))

        # Exploit
        exploit_url = f"{base_url}/search?q={quote(tr.exploit_payload)}"
        r = httpx.get(exploit_url, timeout=5.0)
        exploit_response = r.text
        (run_folder / "exploit_response.json").write_text(
            json.dumps({"status": r.status_code, "body": exploit_response}, indent=2)
        )

        # Oracle (config-driven rule engine)
        verdict, evidence = verify_exploit(
            status_code=r.status_code,
            response_text=exploit_response,
            oracle_config=config.oracle,
        )
        (run_folder / "oracle_verdict.json").write_text(json.dumps(verdict, indent=2))
        (run_folder / "oracle_evidence.json").write_text(json.dumps(evidence, indent=2))
        log.info("oracle_verdict", exploit_success=verdict.get("exploit_success", False))
    finally:
        stop_target(proc)


@click.command()
@click.option(
    "--config",
    "-c",
    "config_path",
    required=True,
    type=click.Path(exists=True, path_type=Path),
    help="Path to YAML run configuration.",
)
@click.option(
    "--log-level",
    default="INFO",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"]),
    help="Logging level.",
)
def main(config_path: Path, log_level: str) -> None:
    """
    Run the Autonomous Cyber-Resilience benchmark experiment.

    Loads config, creates run folder, sets up logging, and orchestrates
    the pipeline: Researcher → Attacker → Oracle → Fixer → Re-Verify → Metrics.

    With target_run configured: runs minimal non-LLM pipeline (recon, exploit, oracle).
    """
    config = load_config(config_path)
    run_folder = create_run_folder(config)
    # Config is at project/configs/run.yaml -> parent.parent = project root
    project_root = config_path.resolve().parent.parent
    run_id = get_run_id(config)

    setup_logging(run_folder=run_folder, log_level=log_level)
    log = structlog.get_logger()
    log.info("run_started", run_id=run_id, run_folder=str(run_folder), config_path=str(config_path))
    if config.target_run:
        _run_minimal_pipeline(config, run_folder, project_root, log)
    else:
        log.info("skipping_minimal_pipeline", reason="target_run not configured")

    log.info("run_completed", run_id=run_id)


if __name__ == "__main__":
    main()
