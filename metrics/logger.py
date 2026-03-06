"""
Structured metrics logging - EtE, EtP, run artifacts.

TODO: CodeCarbon integration
TODO: Emit Energy-to-Exploit (EtE) and Energy-to-Patch (EtP) metrics
TODO: JSON output validation with pydantic
"""

import json
from pathlib import Path


def log_metrics(run_folder: Path, metrics: dict) -> None:
    """
    Write structured metrics to run folder.

    Args:
        run_folder: Path to run folder.
        metrics: Dict of metrics to persist.
    """
    # TODO: CodeCarbon integration - attach energy measurements
    # TODO: Validate metrics with pydantic before write
    path = run_folder / "metrics.json"
    with open(path, "w") as f:
        json.dump(metrics, f, indent=2)
