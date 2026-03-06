## Autonomous Cyber-Resilience – Project Overview & Status

### 1. Project Identity

- **Title**: Autonomous Cyber-Resilience: Benchmarking Multi-Agent LLM Frameworks for Zero-Day Application-Layer Vulnerability Discovery and Verified Patching  
- **Scope**: Research-grade capstone project focused on **closed-loop, multi-agent security workflows** for application-layer vulnerabilities (SQLi, IDOR, XSS) under sandboxed conditions.  
- **Key innovation**:  
  - Treats autonomous security as a **benchmarkable pipeline**, not a single agent.  
  - Introduces energy-aware metrics (**EtE – Energy to Exploit**, **EtP – Energy to Patch**) to reason about the *carbon cost* of autonomous cyber-resilience workflows across different LLM providers.

Target System Architecture (conceptual):

```text
Researcher Agent → Attacker Agent → Verification Oracle → Fixer Agent → Re-Verification → Metrics
```

The whole pipeline is configured and driven via **YAML configs**, with **Python 3.11**, a single CLI entrypoint, and strict modularity.

---

### 2. High-Level Goals

1. **Autonomous vulnerability discovery** on application-layer targets (SQLi, IDOR, XSS).  
2. **Autonomous exploit generation**: PoCs that concretely demonstrate impact.  
3. **Programmatic verification** via a configurable Oracle (status codes, content markers, etc.).  
4. **Autonomous patch generation** that suppresses exploits while preserving functionality.  
5. **Re-verification** after patch to ensure exploit suppression and regression-free behavior.  
6. **Metrics & logging**:
   - Success/failure per step, structured logging, and JSON artifacts.
   - **EtE / EtP** energy metrics (CodeCarbon integration planned).  
7. **Benchmarking across LLM providers** (OpenAI, Claude, DeepSeek, etc.) with a unified agent/orchestration layer.

Constraints:

- Python 3.11 only (enforced at runtime and via `.python-version`).  
- Single entrypoint:
  ```bash
  python -m runner.run_experiment --config configs/run.yaml
  ```  
- No notebook-specific or Colab-specific code inside core modules.  
- All configuration via YAML; **no hard-coded paths**.  
- Runs write artifacts into per-run folders under a configurable `drive_root` (for Colab: Google Drive).

---

### 3. What Has Been Implemented So Far

This section describes **concrete modules** and behavior that are already working.

#### 3.1 Project Scaffolding & Packaging

- **Repository layout**:
  - `runner/` – experiment orchestration and CLI entrypoint.
  - `config/` – pydantic schemas and YAML loader.
  - `targets/` – vulnerable targets and target runner.
  - `agents/` – placeholder Researcher/Attacker/Fixer agents.
  - `oracle/` – verification Oracle (now config-driven).
  - `metrics/` – metrics logging placeholders.
  - `utils/` – logging and run-folder utilities.
  - `tests/` – pytest smoke tests.
  - `scripts/` – utility scripts (`setup_dev.sh`, `print_latest_run.py`).
  - `colab/` – Colab execution guide.
  - `configs/` – YAML run configs (`run.yaml`, `run_colab.yaml`).

- **Packaging**:
  - `pyproject.toml` with:
    - `requires-python = ">=3.11"`  
    - Package discovery for `agents`, `config`, `metrics`, `oracle`, `runner`, `targets`, `utils`.
  - `.python-version` pinned to **3.11.14** for pyenv-aware environments.

- **Dependencies** (`requirements.txt`):
  - Core: `pydantic`, `PyYAML`, `click`, `structlog`, `httpx`, `flask`, `pytest`.
  - CodeCarbon commented out for now (to be enabled when EtE/EtP integration begins).

#### 3.2 Config System (YAML + Pydantic)

- **Schema** (`config/schema.py`):
  - `PathsConfig` – `drive_root`, `runs_dir`, `datasets_dir`, `targets_dir`, `reports_dir`.  
  - `RunSectionConfig` – `run_id` (optional), `experiment_name`.  
  - `TargetSpec` – type (`"sqli" | "idor" | "xss"`), `path`, `port`, `name`.  
  - `TargetRunConfig` – single active target with:
    - `name`, `type`, `path`, `port`, `exploit_payload`.  
  - **`OracleConfig`** – **new** config-driven rule engine:
    - `success_status_codes: list[int] = [200]`
    - `fail_status_codes: list[int] = [401, 403, 404, 500]`
    - `success_contains_any: list[str]`
    - `success_contains_all: list[str] | None`
    - `fail_contains_any: list[str] | None`
    - `max_snippet_len: int = 200`
  - `SandboxConfig` – placeholder for udocker integration.  
  - `MetricsConfig` – placeholder for metrics formats and CodeCarbon toggle.  
  - `RunConfig` – aggregates all sections plus a single `target_run` and `oracle`.

- **Loader** (`config/loader.py`):
  - `load_config(path) -> RunConfig`:
    - Validates YAML against `RunConfig`.
    - Raises clear errors for missing files or invalid structure.

- **Configs**:
  - `configs/run.yaml` – default local config (drive_root = `./drive`).
  - `configs/run_colab.yaml` – **Colab-specific** config with:
    - `paths.drive_root = "/content/drive/MyDrive/AgenticSecurity"`.

#### 3.3 Run Folder Management & Logging

- **Run folder** (`utils/run_folder.py`):
  - `create_run_folder(config)`:
    - Creates `{drive_root}/{runs_dir}/{run_id}/`  
    - Uses `run_id` from config if present, otherwise generates a short UUID.
  - `get_run_id(config)` currently generates a new ID if `run.run_id` is missing (note: we will likely sync this with `create_run_folder` later so they always match).

- **Structured logging** (`utils/logging_config.py`):
  - Uses `structlog` with:
    - Context vars, log levels, timestamps.
    - Console or JSON renderer depending on TTY.
  - Logs to:
    - `stdout`  
    - `run.log` inside the run folder.
  - Adjusted for Structlog 24.x to avoid processor contract breakage.

#### 3.4 Minimal Vulnerable Target + Runner

- **Flask SQLi Demo** (`targets/flask_sqli_demo/app.py`):
  - SQLite `data.db` with:
    - Table `items(id, name)` containing:
      - `LEAK_MARKER` row specifically for Oracle detection.
  - Endpoints:
    - `GET /health` → `"OK"` with HTTP 200.
    - `GET /` → JSON message (`{"message": "Flask SQLi Demo"}`).
    - `GET /search?q=...` → **intentionally vulnerable** SQLi:
      - Builds SQL string via string concatenation (unsafe).
      - Returns matched rows as JSON: `{"results": [...]}`.

- **Target runner** (`targets/runner.py`):
  - `start_target(target_config, run_folder, project_root) -> Popen`:
    - Starts the Flask app as a subprocess using the configured `path` and `port`.
    - Captures `stdout` / `stderr` into:
      - `target_stdout.log`, `target_stderr.log` in run folder.
  - `wait_for_health(base_url, timeout)`:
    - Polls `/health` until 200 OK or timeout.
  - `stop_target(proc)`:
    - Graceful terminate, then kill if needed.

#### 3.5 Oracle – Config-Driven Rule Engine

- **File:** `oracle/verification.py`

- `verify_exploit(status_code, response_text, oracle_config, headers=None, body_metadata=None) -> (verdict, evidence)`:
  - Uses `OracleConfig` to evaluate:
    - Status code success/failure.
    - Presence/absence of content markers.
  - **Verdict** (`oracle_verdict.json`):
    - `exploit_success: bool`
    - `reason: str`
    - `status_code: int`
  - **Evidence** (`oracle_evidence.json`):
    - `matched_markers: list[str]`
    - `snippet: str` (bounded by `max_snippet_len`)
  - For the SQLi demo, config is:
    - `success_status_codes: [200]`
    - `success_contains_any: ["LEAK_MARKER"]`
  - This keeps the original behavior: exploit success is defined by seeing `LEAK_MARKER` in a 200-OK response.

- `verify_patch(...)`:
  - Stub implementation for future patch/regression checking.

#### 3.6 Runner – Minimal End-to-End Non-LLM Pipeline

- **File:** `runner/run_experiment.py`

Behavior:

1. Enforces **Python 3.11+** at startup.
2. Loads config via `load_config`.
3. Creates run folder.
4. Configures logging to stdout + `run.log`.
5. If `target_run` is defined:
   - Starts the Flask target via `targets.runner.start_target`.
   - Waits for `/health`.
   - Performs a **recon** step:
     - Hits `/`, `/health`, `/search?q=test`.
     - Writes `recon.json`.
   - Performs an **exploit** step:
     - Calls `/search?q=exploit_payload` (e.g. `' OR '1'='1`).
     - Writes `exploit_response.json` with `status` and `body`.
   - Calls **Oracle**:
     - `verify_exploit(status_code, response_text, config.oracle)`.
     - Writes `oracle_verdict.json` and `oracle_evidence.json`.
   - Stops the target cleanly.

This is a fully working **non-LLM** closed-loop for a single target.

#### 3.7 Tests & Scripts

- **Tests** (`tests/test_smoke.py`, `tests/conftest.py`):
  - Spin up the Flask app at a test port.
  - Confirm `/health` returns 200 and `"OK"`.
  - Confirm SQLi payload yields `LEAK_MARKER` in the response.
  - Confirm the Oracle (with `OracleConfig(success_contains_any=["LEAK_MARKER"])`) marks exploit as successful and returns meaningful evidence.

- **Scripts**:
  - `scripts/print_latest_run.py`:
    - Reads `drive_root` and `runs_dir` from config or CLI args.
    - Finds latest run folder and prints:
      - Run ID
      - File list (names + sizes).
  - `scripts/setup_dev.sh`:
    - Helper for macOS/pyenv environments:
      - Ensures Python 3.11.
      - Attempts SSL/cert fixes and dependency installation (documented, though part of this work was superseded by the `--trusted-host` workaround).

#### 3.8 Colab Support (Documentation-Only)

- **Colab doc** (`colab/README_COLAB.md`):
  - Exact cells to:
    1. Mount Google Drive.
    2. Clone the GitHub repo.
    3. Install requirements.
    4. Use `configs/run_colab.yaml` (drive_root already set).
    5. Run `python -m runner.run_experiment --config configs/run_colab.yaml`.
    6. Inspect runs via `scripts/print_latest_run.py` and listing folders.
  - Importantly: **no Colab-specific imports** are present in core modules.

---

### 4. What Still Needs to Be Done (Roadmap)

Below is a non-exhaustive, prioritized roadmap.

#### 4.1 Agent Logic & LLM Integration

- **Researcher Agent** (`agents/researcher.py`):
  - Implement actual LLM calls (OpenAI/Claude/DeepSeek) to:
    - Analyze target documentation / source (if available).
    - Propose candidate injection points and routes.
  - Output structured findings (e.g. endpoints, parameters, vulnerability hypotheses).

- **Attacker Agent** (`agents/attacker.py`):
  - Use the Researcher output + target recon to:
    - Generate concrete PoC payloads for SQLi, IDOR, XSS.
    - Decide sequences of HTTP actions (e.g., login → exploit).
  - Output machine-consumable exploit specifications.

- **Fixer Agent** (`agents/fixer.py`):
  - Given verified exploit + code context:
    - Suggest patches (sanitization, ORM queries, authorization checks, etc.).
    - Preserve functional correctness (no regression on non-malicious traffic).
  - Integrate with:
    - Git-like patch representation or direct file modifications inside the sandbox.

- **Multi-provider LLM abstraction**:
  - Implement a small LLM client layer (e.g. `llm/client.py`) that:
    - Switches providers via config (`llm.provider`, `llm.model`).
    - Handles rate limits, retries, and cost/energy tracking hooks.

#### 4.2 Sandbox / udocker Integration

- Implement **udocker-based** target execution:
  - Wrap the current Flask target (and future targets) in containers.
  - Expose only localhost ports, with strict resource/time limits.
  - Ensure the Oracle interacts solely with containerized targets.

- Extend `SandboxConfig` to:
  - Point to image names, environment variables, entrypoints.
  - Control network/FS exposure for the target.

#### 4.3 Metrics: EtE / EtP and Benchmarking

- **CodeCarbon integration**:
  - Wrap key pipeline segments:
    - Researcher + Attacker (EtE)
    - Fixer + Re-verification (EtP)
  - Emit:
    - Energy consumption per stage.
    - Carbon equivalent per stage.
  - Link metrics to:
    - LLM provider & model.
    - Target type (SQLi, IDOR, XSS).

- **Benchmark runner extensions**:
  - Run **multiple configs** in series:
    - Different providers (OpenAI, Claude, DeepSeek).
    - Different models.
    - Different targets.
  - Aggregate metrics into:
    - JSON/CSV reports in `reports/`.
    - Possibly a small HTML summary for quick visual inspection.

#### 4.4 Targets & Oracle Extensions

- Add more **targets**:
  - IDOR demo app (simple multi-user resource access).
  - XSS demo app (reflected and/or stored XSS).
  - Maybe a small multi-endpoint REST app (more realistic).

- Extend OracleConfig and implementation:
  - IDOR:
    - Markers based on unauthorized data access patterns or user IDs.
  - XSS:
    - Markers in HTML/JS payloads (e.g., `<script>alert('XSS_MARKER')</script>`).
  - Regression checks:
    - HTTP 2xx for healthy behavior on benign inputs.
    - Optional snapshot tests (before/after patch).

#### 4.5 Runner & CLI Enhancements

- Make runner more flexible:
  - Flags to skip certain stages (e.g., only recon, only exploit, only verify).
  - Multiple runs per config (for randomness/variance).

- Config-driven:
  - Timeouts, retry policies, LLM prompt templates.
  - Discrete seeds for reproducibility.

#### 4.6 Documentation & Reporting

- Deeper documentation:
  - Architectural diagrams.
  - Threat model for the benchmark environment.
  - Limitations and safe-use guidelines.

- Example reports:
  - Sample outputs for successful and failed exploits.
  - Example EtE/EtP tables comparing models.

---

### 5. Challenges Encountered (and Their Status)

#### 5.1 Python & Environment Management

- **Issue**: Project strictly requires Python 3.11, but the machine had multiple versions (3.9, 3.10, 3.12), causing:
  - `ModuleNotFoundError` (e.g., `httpx` not installed in that interpreter).
  - Confusion over which `python` / `pip` was active in each shell.

- **Mitigation**:
  - Enforced 3.11+ at runtime in `runner/run_experiment.py`.
  - Added `.python-version` = `3.11.14` and updated `~/.pyenv/version` (global) so pyenv picks 3.11 automatically.
  - Documented in `README.md` how to install/use pyenv 3.11.

- **Status**: **Resolved** from the project’s perspective, but users still need to keep pyenv correctly initialized in `~/.zshrc`.

#### 5.2 SSL / Certificate Errors on macOS

- **Issue**: `pip install` with system Python hit:
  - `SSLCertVerificationError('OSStatus -26276')` against PyPI.

- **Causes**:
  - macOS trust store and Python/OpenSSL mismatch.
  - Corporate proxy/network or keychain restrictions (common on macOS).

- **Mitigation**:
  - Switched to **pyenv 3.11** and used:
    ```bash
    python -m pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt
    ```
  - This bypasses certificate validation *for installation only*.
  - Documented this approach clearly in `README.md`.

- **Status**: **Workable workaround**; the root macOS cert issue might still exist for system Python but no longer blocks this project.

#### 5.3 Structlog API Changes

- **Issue**: Initial logging setup assumed a different structlog processor contract, leading to:
  - Errors like `'str' object has no attribute 'pop'` inside processors.

- **Mitigation**:
  - Simplified structlog configuration:
    - Kept processors that operate on dicts.
    - Ensured final renderer is last in the chain.
    - Removed incompatible `ExceptionRenderer` positioning.

- **Status**: **Resolved**; structured logging now works with structlog 24.x.

#### 5.4 Sandbox / Network Restrictions in Dev Environment

- **Issue**: Flask target health checks and pytest had issues when:
  - Network access/localhost were restricted in the sandbox.

- **Mitigation**:
  - For tests and experiment runs using the assistant, explicitly requested network permissions when needed.
  - Confirmed that, in a normal user environment (outside the tool sandbox), Flask + httpx works as intended.

- **Status**: **Resolved** for your local machine; still something to be mindful of when using heavily sandboxed CI environments.

---

### 6. Remaining/Open Challenges

1. **Safety & Scope Control**:
   - Ensuring agents never go beyond sandbox boundaries.
   - Preventing accidental targeting of external hosts.

2. **Complexity of Full Closed-Loop Patching**:
   - Getting the Fixer Agent to produce patches that:
     - Apply cleanly (no syntax/logic errors).
     - Don’t introduce new vulnerabilities.
     - Don’t regress existing behavior.

3. **Robust Benchmarking**:
   - Designing experiments that are:
     - Fair across LLM providers.
     - Reproducible (seeded randomness).
     - Comparable across targets and providers.

4. **Energy Measurement Accuracy (EtE / EtP)**:
   - Accurately attributing energy consumption to:
     - LLM calls (remote).
     - Local orchestration and sandboxing.
   - Dealing with noisy measurements and sharing methodology transparently.

---

### 7. Division of Responsibilities: You vs. Agentic IDE

This section explicitly separates what **Cursor/LLM agents** should handle vs. what **you**, as the human researcher, must do.

#### 7.1 Responsibilities for the Agentic IDE (Cursor, future agents)

The IDE + LLM agents should primarily handle:

- **Code creation and refactoring**:
  - Implementing new modules for agents, oracle, metrics, sandboxing.
  - Refactoring runner, targets, and utils for clarity and modularity.
  - Adding and maintaining tests (pytest) and type hints.

- **Configuration plumbing**:
  - Extending `RunConfig` and YAML schema safely.
  - Ensuring no hard-coded paths, everything driven by config.

- **Orchestration logic**:
  - Building out orchestration for:
    - Researcher → Attacker → Oracle → Fixer → Re-Verification.
  - Implementing error handling and retries.

- **LLM Integration Logic (but not secrets)**:
  - Abstract clients for OpenAI, Claude, DeepSeek, etc.
  - Prompt templates, response parsing, confidence scoring.
  - Caching of results and token/latency measurement.

- **Sandbox & Oracle Implementation**:
  - Implementing udocker integration in code (once you provide image names/constraints).
  - Extending Oracle rules and configuration options.

- **Metrics & Reporting**:
  - Integrating CodeCarbon APIs (given the library is installed).
  - Writing JSON/CSV/HTML-based reports.
  - Providing helper scripts to summarize benchmarks.

- **Documentation & Examples**:
  - Writing/maintaining markdown docs like this one.
  - Creating example configs, command snippets, and troubleshooting sections.

#### 7.2 Responsibilities for You (Human Researcher)

These are tasks that **cannot** or **should not** be automated by an IDE/LLM:

- **Credentials & Secrets**:
  - Creating and managing API keys:
    - OpenAI, Anthropic (Claude), DeepSeek, etc.
  - Setting them via environment variables or secret stores:
    - e.g., `export OPENAI_API_KEY=...`  
    - Never committing them to the repo.

- **Environment & OS-Level Setup**:
  - Installing pyenv and Python 3.11 on your machine.  
  - Fixing OS certificate/keychain issues (e.g., macOS SSL trust):
    - Running `Install Certificates.command` if needed.
    - Coordinating with corporate IT/proxy if required.
  - Installing system tools:
    - Docker/udocker or any container runtime.
    - SQLite / DB tools if needed.

- **Colab & Cloud Execution**:
  - Actually running notebooks in Colab:
    - Mounting your own Google Drive.
    - Choosing the appropriate Drive folder (e.g., `MyDrive/AgenticSecurity`).
  - Controlling cloud spend and API rate limits:
    - Deciding which experiments to run, how many times, on which models.

- **Drive Structure & Data Curation**:
  - Creating and organizing:
    - `runs/`, `datasets/`, `targets/`, `reports/` inside your Drive.
  - Uploading or approving upload of additional targets and datasets.
  - Deleting/archiving old runs to manage storage.

- **Ethical & Safety Decisions**:
  - Deciding **which targets** are acceptable for testing.
  - Ensuring all experiments are limited to:
    - Owned/consented systems.
    - Sandboxed, non-production environments.
  - Documenting and enforcing safe use policies.

- **Research Design & Interpretation**:
  - Designing the benchmark:
    - Which vulnerability types, which targets, which LLMs.
    - How many runs per condition.
  - Interpreting results:
    - Understanding **why** some models succeed/fail.
    - Analyzing tradeoffs between EtE/EtP, exploit coverage, and patch correctness.

- **Manual Debugging & Validation**:
  - When something looks suspicious (e.g., patch seems unsafe), manually:
    - Reading the generated code.
    - Running local tests and verifying correctness.
  - Approving or rejecting automated patches before they’re considered “valid” for research claims.

---

### 8. Current Status Snapshot

- **Core scaffold**: Complete and stable.  
- **Non-LLM SQLi demo pipeline**: Working end-to-end (target → exploit → Oracle → artifacts).  
- **Oracle**: Upgraded to a strict, config-driven rule engine.  
- **Testing**: Smoke tests passing for target + Oracle behavior.  
- **Colab integration**: Documented execution flow with a dedicated config and helper script.  
- **Environment**: Python 3.11 pinned; pyenv + SSL workarounds documented and functioning for your machine.

**Next immediate steps** (recommended):

- **Complete full Colab end-to-end validation of SQLi workflow**  
  - Run the pipeline in Colab using `configs/run_colab.yaml`.  
  - Confirm that artifacts (`recon.json`, `exploit_response.json`, `oracle_verdict.json`, `oracle_evidence.json`, logs) are written under `/content/drive/MyDrive/AgenticSecurity/runs/<run_id>/`.  
  - Validate that `scripts/print_latest_run.py` works in Colab with `--drive-root /content/drive/MyDrive/AgenticSecurity`.

- **Implement IDOR demo target**  
  - New Flask (or similar) demo under `targets/idor_demo/` with:
    - **Deterministic exploit logic** (e.g., predictable object IDs where unauthorized user can read another user’s resource).  
    - **Legitimate-access control verification** (Oracle rules to check correct 403/404 for unauthorized access and 200 for authorized access).  
    - **Post-patch validation logic** (Oracle rules to ensure exploit is blocked while legitimate access still works).

- **Implement Reflected XSS (R-XSS) demo target**  
  - New demo under `targets/xss_demo/` with:
    - **Reflected injection verification** (Oracle checks for presence/absence of an `XSS_MARKER` in rendered HTML/JS).  
    - **Post-patch sanitization validation** (Oracle ensures that after patch, user-controlled inputs are correctly escaped and no longer execute).

- **Formalize Patch Oracle (PO)**  
  - Extend `oracle/verification.py` (or a new `patch_oracle.py`) to:
    - Verify **exploit no longer succeeds** after patch.  
    - Verify **legitimate functionality is preserved** (e.g., health checks, benign use cases).  
    - Ensure **patch diff is stored as an artifact** (e.g., `patch_diff.txt` or `patch.json`), derived from the Fixer Agent output or a VCS diff.

- **Generalize Target Registry**  
  - Introduce a `targets/registry.py` (or config-driven registry) that enumerates all benchmark cases:
    - SQLi (current demo) – with multiple difficulty levels if desired.  
    - IDOR demo cases.  
    - Reflected XSS demo cases.  
  - Support **up to 9 benchmark combinations** (e.g., 3 vuln classes × 3 target variants) with consistent config/Oracle wiring.

- **Implement benchmark runner**  
  - Extend `runner/run_experiment.py` or create `runner/benchmark_runner.py` to:
    - Iterate over a set of configs (targets × models × providers).  
    - Collect metrics (success rates, EtE/EtP once integrated, run durations).  
    - Write aggregated benchmark results into `reports/` (JSON/CSV), ready for analysis.

---

### 9. Progress Status

- **Overall completion**: ~45%

- **Breakdown**:
  - **Architecture design**: 100%  
  - **Project scaffold & CLI framework**: 100%  
  - **SQL Injection demo + Exploit Oracle (content-based)**: 100%  
  - **IDOR & Reflected XSS targets**: 0% (planned next)  
  - **Patch Oracle (PO)**: ~30% (design stubbed, implementation pending)  
  - **LLM multi-agent integration (Researcher/Attacker/Fixer)**: 0% (placeholders only)  
  - **Sustainability metrics (CodeCarbon / EtE / EtP)**: 0% (design planned, no code yet)  
  - **Benchmark execution (multi-target, multi-LLM)**: 0% (runner extensions pending)

This document should give future you (and any future pair-programmer, human or AI) a clear picture of where the project stands, the design philosophy, and how to safely extend it.

