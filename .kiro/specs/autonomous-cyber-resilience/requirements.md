# Requirements: Autonomous Cyber-Resilience System

## 1. Project Overview

### 1.1 Project Identity
A research-grade benchmarking system for evaluating multi-agent LLM frameworks in autonomous vulnerability discovery and verified patching workflows. The system focuses on application-layer vulnerabilities (SQLi, IDOR, XSS) with energy-aware sustainability metrics.

### 1.2 Core Innovation
- Treats autonomous security as a benchmarkable pipeline, not a single agent
- Introduces Energy-to-Exploit (EtE) and Energy-to-Patch (EtP) metrics to quantify carbon cost of cyber-resilience workflows
- Provides programmatic verification via configurable Oracle system

### 1.3 Target Architecture
```
Researcher Agent → Attacker Agent → Verification Oracle → Fixer Agent → Re-Verification → Metrics
```

## 2. Functional Requirements

### 2.1 Configuration System [COMPLETED]

**User Story**: As a researcher, I need a flexible YAML-based configuration system so I can run experiments across different environments (local, Colab) without code changes.

**Acceptance Criteria**:
- [x] 2.1.1 YAML configuration loader with Pydantic validation
- [x] 2.1.2 PathsConfig for drive_root, runs_dir, datasets_dir, targets_dir, reports_dir
- [x] 2.1.3 RunSectionConfig with run_id and experiment_name
- [x] 2.1.4 TargetSpec supporting sqli, idor, xss types
- [x] 2.1.5 OracleConfig with configurable success/fail rules
- [x] 2.1.6 LLMConfig for provider and model selection
- [x] 2.1.7 SandboxConfig for udocker integration
- [x] 2.1.8 MetricsConfig for output format and CodeCarbon toggle
- [x] 2.1.9 Separate configs for local (run.yaml) and Colab (run_colab.yaml)

### 2.2 Run Management [COMPLETED]

**User Story**: As a researcher, I need isolated run folders with unique IDs so I can track and compare multiple experiment executions.

**Acceptance Criteria**:
- [x] 2.2.1 Create run folder under {drive_root}/{runs_dir}/{run_id}/
- [x] 2.2.2 Auto-generate run_id if not provided in config
- [x] 2.2.3 Store all run artifacts in isolated run folder
- [x] 2.2.4 Structured logging to stdout and run.log

### 2.3 Vulnerable Target System [COMPLETED]

**User Story**: As a researcher, I need vulnerable target applications so I can benchmark exploit discovery and patching capabilities.

**Acceptance Criteria**:
- [x] 2.3.1 Flask SQLi demo with intentional SQL injection vulnerability
- [x] 2.3.2 Database seeded with LEAK_MARKER for exploit detection
- [x] 2.3.3 Health endpoint for readiness checks
- [x] 2.3.4 Search endpoint with vulnerable string concatenation
- [x] 2.3.5 Target runner to start/stop apps as subprocesses
- [x] 2.3.6 Capture stdout/stderr to run folder logs
- [x] 2.3.7 Health check polling with configurable timeout

### 2.4 Verification Oracle [COMPLETED]

**User Story**: As a researcher, I need a config-driven verification oracle so I can programmatically validate exploit success across different vulnerability types.

**Acceptance Criteria**:
- [x] 2.4.1 Config-driven rule engine for exploit verification
- [x] 2.4.2 Status code success/fail rules
- [x] 2.4.3 Content marker detection (success_contains_any, success_contains_all, fail_contains_any)
- [x] 2.4.4 Verdict output with exploit_success, reason, status_code
- [x] 2.4.5 Evidence output with matched_markers and response snippet
- [x] 2.4.6 Configurable snippet length for evidence
- [x] 2.4.7 Structured logging of verification results

### 2.5 Minimal Pipeline [COMPLETED]

**User Story**: As a researcher, I need a working end-to-end non-LLM pipeline so I can validate the infrastructure before integrating LLM agents.

**Acceptance Criteria**:
- [x] 2.5.1 Single CLI entrypoint: python -m runner.run_experiment --config
- [x] 2.5.2 Python 3.11+ enforcement at runtime
- [x] 2.5.3 Recon step hitting /, /health, /search endpoints
- [x] 2.5.4 Exploit step with configurable payload
- [x] 2.5.5 Oracle verification with verdict and evidence artifacts
- [x] 2.5.6 Clean target shutdown after execution
- [x] 2.5.7 All artifacts written to run folder (recon.json, exploit_response.json, oracle_verdict.json, oracle_evidence.json)

### 2.6 Testing Infrastructure [COMPLETED]

**User Story**: As a developer, I need automated tests so I can validate core functionality and prevent regressions.

**Acceptance Criteria**:
- [x] 2.6.1 Pytest configuration with test discovery
- [x] 2.6.2 Smoke tests for health endpoint
- [x] 2.6.3 Smoke tests for SQLi exploit triggering LEAK_MARKER
- [x] 2.6.4 Smoke tests for Oracle detection of exploit success
- [x] 2.6.5 Test fixtures for Flask app lifecycle

### 2.7 LLM Agent Integration [NOT STARTED]

**User Story**: As a researcher, I need LLM-powered agents so I can automate vulnerability discovery, exploit generation, and patch creation.

**Acceptance Criteria**:
- [ ] 2.7.1 Researcher Agent: Analyze targets and produce structured findings
- [ ] 2.7.2 Attacker Agent: Generate PoC exploits from findings
- [ ] 2.7.3 Fixer Agent: Generate patches for verified vulnerabilities
- [ ] 2.7.4 Multi-provider LLM client (OpenAI, Claude, DeepSeek)
- [ ] 2.7.5 API key management via environment variables
- [ ] 2.7.6 Rate limiting and retry logic
- [ ] 2.7.7 Structured output parsing from LLM responses
- [ ] 2.7.8 Cost tracking per LLM call

### 2.8 Additional Vulnerability Targets [NOT STARTED]

**User Story**: As a researcher, I need multiple vulnerability types so I can benchmark across different attack surfaces.

**Acceptance Criteria**:
- [ ] 2.8.1 IDOR demo app with multi-user resource access
- [ ] 2.8.2 IDOR Oracle rules for unauthorized access detection
- [ ] 2.8.3 XSS demo app with reflected XSS vulnerability
- [ ] 2.8.4 XSS Oracle rules for script injection detection
- [ ] 2.8.5 Target registry for managing multiple benchmark cases
- [ ] 2.8.6 Support for up to 9 benchmark combinations (3 vuln types × 3 variants)

### 2.9 Patch Verification [NOT STARTED]

**User Story**: As a researcher, I need patch verification so I can validate that fixes suppress exploits without introducing regressions.

**Acceptance Criteria**:
- [ ] 2.9.1 Patch Oracle implementation
- [ ] 2.9.2 Verify exploit suppression after patch
- [ ] 2.9.3 Verify legitimate functionality preservation
- [ ] 2.9.4 Regression test suite for benign inputs
- [ ] 2.9.5 Patch diff artifact storage
- [ ] 2.9.6 Re-verification workflow integration

### 2.10 Sandbox Integration [NOT STARTED]

**User Story**: As a researcher, I need containerized target execution so I can safely run exploits in isolated environments.

**Acceptance Criteria**:
- [ ] 2.10.1 udocker-based target execution
- [ ] 2.10.2 Localhost-only port exposure
- [ ] 2.10.3 Resource and time limits per container
- [ ] 2.10.4 Network and filesystem isolation
- [ ] 2.10.5 Container image configuration via SandboxConfig
- [ ] 2.10.6 Clean container lifecycle management

### 2.11 Energy Metrics (EtE/EtP) [NOT STARTED]

**User Story**: As a researcher, I need energy consumption metrics so I can quantify the carbon cost of autonomous cyber-resilience workflows.

**Acceptance Criteria**:
- [ ] 2.11.1 CodeCarbon integration
- [ ] 2.11.2 Energy-to-Exploit (EtE) measurement for Researcher + Attacker
- [ ] 2.11.3 Energy-to-Patch (EtP) measurement for Fixer + Re-verification
- [ ] 2.11.4 Carbon equivalent calculation per stage
- [ ] 2.11.5 Energy metrics linked to LLM provider and model
- [ ] 2.11.6 Energy metrics linked to target type
- [ ] 2.11.7 Structured metrics output to metrics.json

### 2.12 Benchmark Runner [NOT STARTED]

**User Story**: As a researcher, I need automated benchmark execution so I can compare multiple LLM providers and models across different targets.

**Acceptance Criteria**:
- [ ] 2.12.1 Multi-config batch execution
- [ ] 2.12.2 Iterate over providers (OpenAI, Claude, DeepSeek)
- [ ] 2.12.3 Iterate over models per provider
- [ ] 2.12.4 Iterate over target types (SQLi, IDOR, XSS)
- [ ] 2.12.5 Aggregate success rates per configuration
- [ ] 2.12.6 Aggregate EtE/EtP metrics per configuration
- [ ] 2.12.7 JSON/CSV report generation in reports/
- [ ] 2.12.8 HTML summary report for visual inspection

## 3. Non-Functional Requirements

### 3.1 Environment Constraints [COMPLETED]
- [x] 3.1.1 Python 3.11+ required (enforced at runtime)
- [x] 3.1.2 .python-version file for pyenv compatibility
- [x] 3.1.3 pyproject.toml with requires-python >= 3.11

### 3.2 Portability [COMPLETED]
- [x] 3.2.1 No hardcoded paths in code
- [x] 3.2.2 All paths configurable via YAML
- [x] 3.2.3 Colab-compatible execution (documented)
- [x] 3.2.4 No notebook-specific code in core modules

### 3.3 Modularity [COMPLETED]
- [x] 3.3.1 Separate packages: agents, config, metrics, oracle, runner, targets, utils
- [x] 3.3.2 Clear separation of concerns
- [x] 3.3.3 Minimal coupling between modules

### 3.4 Logging and Observability [COMPLETED]
- [x] 3.4.1 Structured logging with structlog
- [x] 3.4.2 Console and JSON renderers
- [x] 3.4.3 Per-run log files
- [x] 3.4.4 Context variables for log correlation

### 3.5 Security and Safety [PARTIALLY COMPLETED]
- [x] 3.5.1 Localhost-only target execution
- [x] 3.5.2 No external network access from targets
- [ ] 3.5.3 Container-based isolation (pending udocker)
- [ ] 3.5.4 Resource limits per execution
- [ ] 3.5.5 Timeout enforcement

### 3.6 Reproducibility [PARTIALLY COMPLETED]
- [x] 3.6.1 Deterministic run IDs when specified
- [x] 3.6.2 Config-driven execution
- [ ] 3.6.3 Seeded randomness for LLM calls
- [ ] 3.6.4 Version tracking for dependencies

## 4. Technical Constraints

### 4.1 Dependencies
- Core: pydantic, PyYAML, click, structlog, httpx, flask, pytest
- Future: codecarbon (for energy metrics)
- Future: udocker (for sandboxing)

### 4.2 Development Workflow
- Development: Cursor IDE
- Version control: GitHub
- Execution: Local + Colab
- Artifacts: Google Drive (runs/, datasets/, targets/, reports/)

### 4.3 API Keys (External)
- OpenAI: OPENAI_API_KEY
- Anthropic: ANTHROPIC_API_KEY
- DeepSeek: DEEPSEEK_API_KEY
- Never committed to repository

## 5. Project Status Summary

**Overall Completion**: ~45%

**Completed Components**:
- Configuration system (100%)
- Run management (100%)
- SQLi vulnerable target (100%)
- Verification Oracle (100%)
- Minimal non-LLM pipeline (100%)
- Testing infrastructure (100%)
- Project scaffolding (100%)

**In Progress**:
- None currently

**Not Started**:
- LLM agent integration (0%)
- IDOR and XSS targets (0%)
- Patch verification (0%)
- Sandbox integration (0%)
- Energy metrics (0%)
- Benchmark runner (0%)

## 6. Success Criteria

The project will be considered successful when:
1. All three vulnerability types (SQLi, IDOR, XSS) have working targets and Oracle rules
2. LLM agents can autonomously discover, exploit, and patch vulnerabilities
3. Patch verification confirms exploit suppression without regressions
4. EtE and EtP metrics are collected for all benchmark runs
5. Benchmark runner can compare multiple LLM providers across all targets
6. Results are reproducible and documented
