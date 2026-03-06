"""YAML configuration loader with pydantic validation."""

from pathlib import Path

import yaml
from pydantic import ValidationError

from config.schema import RunConfig


def load_config(config_path: str | Path) -> RunConfig:
    """
    Load and validate run configuration from YAML file.

    Args:
        config_path: Path to YAML config file.

    Returns:
        Validated RunConfig instance.

    Raises:
        FileNotFoundError: If config file does not exist.
        ValidationError: If config does not match schema.
    """
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    with open(path) as f:
        raw = yaml.safe_load(f)

    if raw is None:
        raw = {}

    return RunConfig.model_validate(raw)
