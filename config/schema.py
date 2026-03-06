"""Pydantic schemas for run configuration validation."""

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field


class PathsConfig(BaseModel):
    """Paths configuration - all configurable, no hardcoded values."""

    drive_root: str = "./drive"
    runs_dir: str = "runs"
    datasets_dir: str = "datasets"
    targets_dir: str = "targets"
    reports_dir: str = "reports"


class RunSectionConfig(BaseModel):
    """Run metadata section."""

    run_id: str | None = None
    experiment_name: str = "benchmark_run"


class TargetSpec(BaseModel):
    """Single target application specification."""

    type: Literal["sqli", "idor", "xss"]
    path: str = ""
    port: int = 5000
    name: str = ""


class OracleConfig(BaseModel):
    """Oracle rule engine - config-driven exploit verification."""

    success_status_codes: list[int] = Field(default_factory=lambda: [200])
    fail_status_codes: list[int] = Field(default_factory=lambda: [401, 403, 404, 500])
    success_contains_any: list[str] = Field(default_factory=list)
    success_contains_all: list[str] | None = None
    fail_contains_any: list[str] | None = None
    max_snippet_len: int = 200


class TargetRunConfig(BaseModel):
    """Target run config: name, port, path, exploit payload."""

    name: str
    type: Literal["sqli", "idor", "xss"]
    path: str
    port: int = 5000
    exploit_payload: str = "' OR '1'='1"


class LLMConfig(BaseModel):
    """LLM provider configuration."""

    provider: Literal["openai", "groq", "claude", "deepseek"] = "groq"
    model: str = "llama-3.1-70b-versatile"


class SandboxConfig(BaseModel):
    """Sandbox/udocker configuration."""

    enabled: bool = False
    image: str = ""
    timeout_seconds: int = 300


class MetricsConfig(BaseModel):
    """Metrics and output configuration."""

    codecarbon_enabled: bool = False
    output_format: Literal["json", "csv"] = "json"


class RunConfig(BaseModel):
    """Top-level run configuration - validated against YAML."""

    run: RunSectionConfig = Field(default_factory=RunSectionConfig)
    paths: PathsConfig = Field(default_factory=PathsConfig)
    llm: LLMConfig = Field(default_factory=LLMConfig)
    oracle: OracleConfig = Field(default_factory=OracleConfig)
    targets: list[TargetSpec] = Field(default_factory=list)
    target_run: TargetRunConfig | None = None  # Single target for minimal pipeline
    sandbox: SandboxConfig = Field(default_factory=SandboxConfig)
    metrics: MetricsConfig = Field(default_factory=MetricsConfig)
