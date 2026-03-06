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
from agents.researcher import analyze_target
from agents.attacker import generate_exploits


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


def _run_llm_pipeline(
    config: RunConfig, run_folder: Path, project_root: Path, log: structlog.BoundLogger
) -> None:
    """Full LLM-powered pipeline: Researcher → Attacker → Oracle → Fixer."""
    tr = config.target_run
    if not tr:
        log.info("skipping_llm_pipeline", reason="target_run not configured")
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

        # Researcher Agent: Analyze target for vulnerabilities
        log.info("researcher_agent_starting")
        target_spec = {
            "type": tr.type,
            "name": tr.name,
            "port": tr.port,
            "path": tr.path,
        }
        findings = analyze_target(target_spec, recon, run_folder)
        
        if not findings.get("findings"):
            log.warning("researcher_no_findings", error=findings.get("error"))
            return

        log.info("researcher_findings", count=len(findings["findings"]))

        # Attacker Agent: Generate exploits from findings
        log.info("attacker_agent_starting")
        exploits = generate_exploits(findings, target_spec, run_folder)
        
        if not exploits:
            log.warning("attacker_no_exploits")
            return

        log.info("attacker_exploits", count=len(exploits))

        # Execute exploits and verify with Oracle (with iterative refinement)
        MAX_REFINEMENT_ATTEMPTS = 3
        successful_exploits = []  # Track successful exploits for Fixer
        
        for i, exploit in enumerate(exploits, 1):
            log.info(f"executing_exploit_{i}", endpoint=exploit.get("endpoint"))
            
            current_exploit = exploit
            success = False
            
            # Try exploit with refinement loop
            for attempt in range(1, MAX_REFINEMENT_ATTEMPTS + 1):
                log.info(f"exploit_{i}_attempt_{attempt}", payload=current_exploit.get("payload"))
                
                # Build exploit URL
                endpoint = current_exploit.get("endpoint", "")
                payload = current_exploit.get("payload", "")
                method = current_exploit.get("method", "GET")
                
                if method == "GET":
                    # For GET requests, add payload as query parameter
                    param_name = findings["findings"][current_exploit.get("finding_id", 1) - 1].get("parameter", "q")
                    exploit_url = f"{base_url}{endpoint}?{param_name}={quote(payload)}"
                    
                    try:
                        r = httpx.get(exploit_url, timeout=5.0)
                        
                        # Oracle verification
                        verdict, evidence = verify_exploit(
                            status_code=r.status_code,
                            response_text=r.text,
                            oracle_config=config.oracle,
                        )
                        
                        # Write results for this attempt
                        (run_folder / f"exploit_{i}_attempt_{attempt}_response.json").write_text(
                            json.dumps({"status": r.status_code, "body": r.text[:1000]}, indent=2)
                        )
                        (run_folder / f"exploit_{i}_attempt_{attempt}_verdict.json").write_text(json.dumps(verdict, indent=2))
                        (run_folder / f"exploit_{i}_attempt_{attempt}_evidence.json").write_text(json.dumps(evidence, indent=2))
                        
                        success = verdict.get("exploit_success", False)
                        
                        if success:
                            log.info(
                                f"exploit_{i}_success",
                                attempt=attempt,
                                payload=payload,
                                matched=evidence.get("matched_markers", []),
                            )
                            # Write final successful exploit
                            (run_folder / f"exploit_{i}_final.json").write_text(
                                json.dumps(current_exploit, indent=2)
                            )
                            # Track for Fixer Agent
                            successful_exploits.append({
                                "exploit": current_exploit,
                                "exploit_number": i,
                                "verdict": verdict,
                                "evidence": evidence,
                            })
                            break
                        else:
                            log.info(
                                f"exploit_{i}_failed_attempt_{attempt}",
                                reason=verdict.get("reason"),
                                response_snippet=r.text[:200],
                            )
                            
                            # Try to refine if not last attempt
                            if attempt < MAX_REFINEMENT_ATTEMPTS:
                                from agents.attacker import refine_exploit
                                
                                refined = refine_exploit(
                                    original_exploit=current_exploit,
                                    failure_reason=verdict.get("reason", "unknown"),
                                    response_body=r.text,
                                    target_spec=target_spec,
                                    attempt=attempt + 1,
                                )
                                
                                if refined:
                                    current_exploit = refined
                                    log.info(f"exploit_{i}_refined", new_payload=refined.get("payload"))
                                else:
                                    log.warning(f"exploit_{i}_refinement_failed", attempt=attempt)
                                    break
                        
                    except Exception as e:
                        log.error(f"exploit_{i}_attempt_{attempt}_error", error=str(e))
                        break
            
            if not success:
                log.warning(
                    f"exploit_{i}_all_attempts_failed",
                    total_attempts=attempt,
                    final_payload=current_exploit.get("payload"),
                )

        # Fixer Agent: Generate patches for successful exploits
        if successful_exploits:
            log.info("fixer_agent_starting", successful_exploit_count=len(successful_exploits))
            
            # Read target source code
            target_path = project_root / tr.path
            try:
                target_source = target_path.read_text()
            except Exception as e:
                log.error("fixer_failed_to_read_source", error=str(e), path=str(target_path))
                target_source = "# Source code not available"
            
            # Generate patch for first successful exploit (or all if time permits)
            from agents.fixer import generate_patch
            
            for exploit_info in successful_exploits[:1]:  # Start with first exploit
                exploit_num = exploit_info["exploit_number"]
                log.info(f"fixer_generating_patch_{exploit_num}")
                
                patch = generate_patch(
                    exploit=exploit_info["exploit"],
                    target_spec=target_spec,
                    target_source=target_source,
                    run_folder=run_folder,
                )
                
                if patch.get("patched_code"):
                    log.info(
                        f"fixer_patch_generated_{exploit_num}",
                        root_cause=patch.get("root_cause", "")[:100],
                    )
                else:
                    log.warning(f"fixer_patch_failed_{exploit_num}")
        else:
            log.info("fixer_skipped", reason="no successful exploits to patch")

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
@click.option(
    "--use-llm",
    is_flag=True,
    default=False,
    help="Use LLM-powered agents (Researcher, Attacker, Fixer). Requires API key.",
)
def main(config_path: Path, log_level: str, use_llm: bool) -> None:
    """
    Run the Autonomous Cyber-Resilience benchmark experiment.

    Loads config, creates run folder, sets up logging, and orchestrates
    the pipeline: Researcher → Attacker → Oracle → Fixer → Re-Verify → Metrics.

    With --use-llm: runs full LLM-powered pipeline (requires GROQ_API_KEY).
    Without --use-llm: runs minimal non-LLM pipeline (recon, exploit, oracle).
    """
    config = load_config(config_path)
    run_folder = create_run_folder(config)
    # Config is at project/configs/run.yaml -> parent.parent = project root
    project_root = config_path.resolve().parent.parent
    run_id = get_run_id(config)

    setup_logging(run_folder=run_folder, log_level=log_level)
    log = structlog.get_logger()
    log.info("run_started", run_id=run_id, run_folder=str(run_folder), config_path=str(config_path), use_llm=use_llm)
    
    if config.target_run:
        if use_llm:
            _run_llm_pipeline(config, run_folder, project_root, log)
        else:
            _run_minimal_pipeline(config, run_folder, project_root, log)
    else:
        log.info("skipping_pipeline", reason="target_run not configured")

    log.info("run_completed", run_id=run_id)


if __name__ == "__main__":
    main()
