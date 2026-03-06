"""Run folder creation logic - per execution with run_id."""

import uuid
from pathlib import Path

from config.schema import RunConfig


def create_run_folder(config: RunConfig) -> Path:
    """
    Create run folder for this execution under drive_root/runs_dir.

    Uses config.run.run_id if set; otherwise generates a unique run_id.
    Folder structure: {drive_root}/{runs_dir}/{run_id}/

    Args:
        config: Validated run configuration.

    Returns:
        Path to the created run folder.
    """
    drive_root = Path(config.paths.drive_root)
    runs_dir = config.paths.runs_dir
    run_id = config.run.run_id or str(uuid.uuid4())[:8]

    run_folder = drive_root / runs_dir / run_id
    run_folder.mkdir(parents=True, exist_ok=True)

    return run_folder


def get_run_id(config: RunConfig) -> str:
    """Get run_id (existing or newly generated)."""
    return config.run.run_id or str(uuid.uuid4())[:8]
