# Design: Autonomous Cyber-Resilience System

## 1. System Architecture

### 1.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLI Entrypoint                          │
│              python -m runner.run_experiment                    │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Configuration Layer                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ YAML Loader  │→ │   Pydantic   │→ │  RunConfig   │         │
│  │              │  │  Validation  │  │              │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Orchestration Layer                        │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ Run Folder   │  │   Logging    │  │   Target     │         │
│  │  Management  │  │    Setup     │  │   Runner     │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Agent Pipeline                             │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  Researcher  │→ │   Attacker   │→ │    Oracle    │         │
│  │    Agent     │  │    Agent     │  │ Verification │         │
│  └──────────────┘  └──────────────┘  └──────┬───────┘         │
│                                              │                  │
│                                              ▼                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Metrics    │← │    Patch     │← │    Fixer     │         │
│  │   Logger     │  │    Oracle    │  │    Agent     │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Artifact Storage                           │
│                                                                 │
│  {drive_root}/{runs_dir}/{run_id}/                             │
│    ├── run.log                                                 │
│    ├── recon.json                                              │
│    ├── exploit_response.json                                   │
│    ├── oracle_verdict.json                                     │
│    ├── oracle_evidence.json                                    │
│    ├── patch_diff.txt                                          │
│    ├── metrics.json                                            │
│    ├── target_stdout.log                                       │
│    └── target_stderr.log                                       │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 Module Responsibilities

#### 1.2.1 Configuration Module (config/)
**Status**: COMPLETED

**Responsibilities**:
- Load and validate YAML configuration files
- Provide type-safe config objects via Pydantic
- Support multiple environments (local, Colab)

**Key Components**:
- `schema.py`: Pydantic models for all config sections
- `loader.py`: YAML loading with validation

**Design Decisions**:
- No hardcoded paths - everything configurable
- Strict validation to catch errors early
- Separate configs for different environments

#### 1.2.2 Runner Module (runner/)
**Status**: COMPLETED (minimal pipeline)

**Responsibilities**:
- CLI entrypoint and argument parsing
- Orchestrate agent pipeline execution
- Manage target lifecycle
- Coordinate artifact generation

**Key Components**:
- `run_experiment.py`: Main orchestration logic

**Design Decisions**:
- Single entrypoint for all execution modes
- Python 3.11+ enforcement at startup
- Graceful error handling and cleanup

#### 1.2.3 Targets Module (targets/)
**Status**: PARTIALLY COMPLETED (SQLi only)

**Responsibilities**:
- Provide vulnerable target applications
- Manage target process lifecycle
- Health check and readiness validation

**Key Components**:
- `runner.py`: Target process management
- `flask_sqli_demo/`: SQLi vulnerable app
- Future: `idor_demo/`, `xss_demo/`

**Design Decisions**:
- Targets run as subprocesses, not threads
- Localhost-only binding for safety
- Stdout/stderr captured to run folder
- Health endpoint for readiness checks

#### 1.2.4 Oracle Module (oracle/)
**Status**: COMPLETED (exploit verification)

**Responsibilities**:
- Verify exploit success via config-driven rules
- Verify patch effectiveness (future)
- Generate structured verdict and evidence

**Key Components**:
- `verification.py`: Rule engine implementation

**Design Decisions**:
- Config-driven rules for flexibility
- Separate verdict (boolean decision) and evidence (supporting data)
- Support for multiple rule types: status codes, content markers
- Extensible for different vulnerability types

#### 1.2.5 Agents Module (agents/)
**Status**: NOT STARTED (placeholders only)

**Responsibilities**:
- Researcher: Analyze targets, identify attack surfaces
- Attacker: Generate PoC exploits
- Fixer: Generate patches for verified vulnerabilities

**Key Components**:
- `researcher.py`: Target analysis agent
- `attacker.py`: Exploit generation agent
- `fixer.py`: Patch generation agent

**Design Decisions**:
- Multi-provider LLM support (OpenAI, Claude, DeepSeek)
- Structured input/output for agent chaining
- Cost and latency tracking per agent call
- Retry logic with exponential backoff

#### 1.2.6 Metrics Module (metrics/)
**Status**: NOT STARTED (placeholder only)

**Responsibilities**:
- Collect and persist run metrics
- Integrate CodeCarbon for energy measurement
- Calculate EtE and EtP metrics

**Key Components**:
- `logger.py`: Metrics persistence

**Design Decisions**:
- JSON output for machine readability
- Pydantic validation for metrics schema
- Per-stage energy measurement
- Link metrics to LLM provider, model, and target type

#### 1.2.7 Utils Module (utils/)
**Status**: COMPLETED

**Responsibilities**:
- Run folder creation and management
- Structured logging configuration

**Key Components**:
- `run_folder.py`: Run folder utilities
- `logging_config.py`: Structlog setup

**Design Decisions**:
- Unique run IDs for isolation
- Structured logging with context variables
- Console and file logging

## 2. Data Flow

### 2.1 Current Minimal Pipeline (Non-LLM)

```
1. Load Config
   ↓
2. Create Run Folder
   ↓
3. Setup Logging
   ↓
4. Start Target (subprocess)
   ↓
5. Wait for Health Check
   ↓
6. Recon (GET /, /health, /search?q=test)
   ↓ (write recon.json)
7. Exploit (GET /search?q={payload})
   ↓ (write exploit_response.json)
8. Oracle Verification
   ↓ (write oracle_verdict.json, oracle_evidence.json)
9. Stop Target
   ↓
10. Complete
```

### 2.2 Future Full Pipeline (With LLM Agents)

```
1. Load Config
   ↓
2. Create Run Folder
   ↓
3. Setup Logging
   ↓
4. Start Target (in sandbox)
   ↓
5. Researcher Agent
   │  - Analyze target spec/source
   │  - Identify attack surfaces
   │  - Output: findings.json
   ↓
6. Attacker Agent
   │  - Consume findings
   │  - Generate PoC exploits
   │  - Output: exploits.json
   ↓
7. Execute Exploits
   │  - Run each exploit against target
   │  - Capture responses
   ↓
8. Exploit Oracle
   │  - Verify exploit success
   │  - Output: oracle_verdict.json, oracle_evidence.json
   ↓
9. Fixer Agent (if exploit succeeded)
   │  - Analyze vulnerability
   │  - Generate patch
   │  - Output: patch_diff.txt
   ↓
10. Apply Patch
   │  - Restart target with patch
   ↓
11. Patch Oracle
   │  - Re-run exploit (should fail)
   │  - Run regression tests (should pass)
   │  - Output: patch_verification.json
   ↓
12. Metrics Collection
   │  - Calculate EtE, EtP
   │  - Output: metrics.json
   ↓
13. Stop Target
   ↓
14. Complete
```

## 3. Configuration Design

### 3.1 Configuration Schema

The configuration system uses Pydantic for validation and type safety. All configuration is loaded from YAML files.

**Top-Level Structure**:
```yaml
run:           # Run metadata
paths:         # File system paths
llm:           # LLM provider config
oracle:        # Oracle rules
targets:       # Target registry
target_run:    # Single target for minimal pipeline
sandbox:       # Container config
metrics:       # Metrics output config
```

### 3.2 Oracle Configuration

The Oracle uses a rule-based system for exploit verification:

**Status Code Rules**:
- `success_status_codes`: List of HTTP codes indicating potential success
- `fail_status_codes`: List of HTTP codes indicating definite failure

**Content Marker Rules**:
- `success_contains_any`: Exploit succeeds if ANY marker present
- `success_contains_all`: Exploit succeeds only if ALL markers present
- `fail_contains_any`: Exploit fails if ANY marker present

**Evidence Configuration**:
- `max_snippet_len`: Maximum response snippet length for evidence

**Evaluation Logic**:
1. Check fail_status_codes → immediate failure
2. Check fail_contains_any → immediate failure
3. Check success_status_codes → required for success
4. Check success_contains_all → all must be present
5. Check success_contains_any → at least one must be present

### 3.3 Target Configuration

**Target Registry** (targets list):
- Defines all available targets
- Used for benchmark iteration

**Target Run** (target_run):
- Specifies single target for execution
- Includes exploit payload
- Used in minimal pipeline

## 4. Oracle Design

### 4.1 Exploit Oracle

**Purpose**: Verify whether an exploit successfully triggered a vulnerability.

**Input**:
- HTTP status code
- Response body text
- Optional: headers, body metadata
- Oracle configuration

**Output**:
- **Verdict**: `{exploit_success: bool, reason: str, status_code: int}`
- **Evidence**: `{matched_markers: list[str], snippet: str}`

**Design Principles**:
- Config-driven for flexibility across vulnerability types
- Separate verdict (decision) from evidence (supporting data)
- Deterministic evaluation for reproducibility
- Structured logging for debugging

### 4.2 Patch Oracle (Future)

**Purpose**: Verify that a patch suppresses the exploit without introducing regressions.

**Input**:
- Original exploit specification
- Patch specification
- Target configuration

**Output**:
- `{suppressed: bool, regression: bool, evidence: dict}`

**Verification Steps**:
1. Re-run original exploit → should fail
2. Run benign test cases → should pass
3. Check for new vulnerabilities → should find none

## 5. Agent Design (Future)

### 5.1 LLM Client Abstraction

**Purpose**: Provide unified interface for multiple LLM providers.

**Interface**:
```python
class LLMClient:
    def __init__(self, provider: str, model: str, api_key: str)
    def call(self, prompt: str, system: str = None) -> LLMResponse
    def call_structured(self, prompt: str, schema: dict) -> dict
```

**Features**:
- Provider switching (OpenAI, Claude, DeepSeek)
- Rate limiting and retry logic
- Cost tracking per call
- Latency measurement
- Response caching (optional)

### 5.2 Researcher Agent

**Purpose**: Analyze targets and identify potential vulnerabilities.

**Input**:
- Target specification (type, endpoints, source code if available)
- Target recon data (from initial HTTP probes)

**Output**:
```json
{
  "findings": [
    {
      "endpoint": "/search",
      "parameter": "q",
      "vulnerability_type": "sqli",
      "confidence": 0.9,
      "reasoning": "String concatenation in SQL query"
    }
  ]
}
```

**LLM Prompt Strategy**:
- System: "You are a security researcher analyzing web applications..."
- User: Provide target spec, recon data, ask for vulnerability analysis
- Request structured JSON output

### 5.3 Attacker Agent

**Purpose**: Generate concrete PoC exploits from findings.

**Input**:
- Researcher findings
- Target base URL and configuration

**Output**:
```json
{
  "exploits": [
    {
      "finding_id": "...",
      "method": "GET",
      "endpoint": "/search",
      "payload": "' OR '1'='1",
      "expected_marker": "LEAK_MARKER"
    }
  ]
}
```

**LLM Prompt Strategy**:
- System: "You are a penetration tester generating PoC exploits..."
- User: Provide findings, ask for exploit payloads
- Request structured JSON output with specific payload formats

### 5.4 Fixer Agent

**Purpose**: Generate patches for verified vulnerabilities.

**Input**:
- Verified exploit specification
- Target source code (if available)
- Vulnerability type

**Output**:
```json
{
  "patch_type": "code_change",
  "file": "app.py",
  "diff": "...",
  "description": "Replace string concatenation with parameterized query",
  "testing_notes": "Verify benign searches still work"
}
```

**LLM Prompt Strategy**:
- System: "You are a security engineer fixing vulnerabilities..."
- User: Provide exploit details, source code, ask for patch
- Request structured JSON output with diff format

## 6. Metrics Design (Future)

### 6.1 Energy Metrics

**Energy-to-Exploit (EtE)**:
- Measures energy consumed from start to verified exploit
- Includes: Researcher Agent + Attacker Agent + Oracle
- Tracked per LLM provider, model, and target type

**Energy-to-Patch (EtP)**:
- Measures energy consumed from verified exploit to verified patch
- Includes: Fixer Agent + Patch Oracle
- Tracked per LLM provider, model, and target type

**Implementation**:
- Use CodeCarbon library
- Wrap agent calls with energy tracking
- Emit structured metrics to metrics.json

### 6.2 Success Metrics

**Per Run**:
- Exploit success rate (binary)
- Patch success rate (binary)
- Time to exploit
- Time to patch
- LLM token usage
- LLM cost

**Aggregate (Benchmark)**:
- Success rate per provider/model/target
- Average EtE per provider/model/target
- Average EtP per provider/model/target
- Cost efficiency (success per dollar)
- Energy efficiency (success per kWh)

## 7. Sandbox Design (Future)

### 7.1 Container Strategy

**Technology**: udocker (userspace Docker, no root required)

**Isolation**:
- Network: localhost only, no external access
- Filesystem: read-only except for temp directories
- Resources: CPU and memory limits
- Time: execution timeout

**Lifecycle**:
1. Pull/build container image
2. Start container with target app
3. Wait for health check
4. Execute exploit
5. Stop and remove container

### 7.2 Security Considerations

**Threat Model**:
- Malicious LLM-generated exploits
- Resource exhaustion attacks
- Network escape attempts

**Mitigations**:
- Strict network isolation
- Resource limits
- Timeout enforcement
- No privileged operations
- Audit logging

## 8. Benchmark Runner Design (Future)

### 8.1 Batch Execution

**Input**: List of configurations
- Providers: [openai, claude, deepseek]
- Models per provider: [gpt-4, gpt-3.5-turbo], [claude-3-opus, claude-3-sonnet], [deepseek-coder]
- Targets: [sqli, idor, xss]

**Execution**:
- Iterate over all combinations
- Run each configuration N times for variance
- Collect metrics per run
- Aggregate results

**Output**:
- `benchmark_results.json`: Raw data per run
- `benchmark_summary.csv`: Aggregated metrics
- `benchmark_report.html`: Visual summary

### 8.2 Reproducibility

**Requirements**:
- Deterministic run IDs
- Seeded randomness for LLM calls
- Version tracking for dependencies
- Config snapshot per run

## 9. Error Handling

### 9.1 Target Failures

**Scenarios**:
- Target fails to start
- Health check timeout
- Target crashes during exploit

**Handling**:
- Log error with context
- Write error artifact to run folder
- Clean up target process
- Mark run as failed in metrics

### 9.2 Agent Failures

**Scenarios**:
- LLM API timeout
- LLM API rate limit
- Invalid LLM response format
- LLM refuses to generate exploit/patch

**Handling**:
- Retry with exponential backoff (up to 3 times)
- Log failure reason
- Fall back to next agent strategy (if available)
- Mark run as failed if all retries exhausted

### 9.3 Oracle Failures

**Scenarios**:
- Ambiguous response (neither clear success nor failure)
- Missing expected markers
- Unexpected status codes

**Handling**:
- Log ambiguity with full context
- Apply conservative verdict (prefer false negative over false positive)
- Include uncertainty in evidence

## 10. Testing Strategy

### 10.1 Unit Tests

**Coverage**:
- Config loading and validation
- Oracle rule evaluation
- Run folder creation
- Target process management

**Framework**: pytest

### 10.2 Integration Tests

**Coverage**:
- End-to-end minimal pipeline
- Target startup and health check
- Exploit execution and Oracle verification
- Artifact generation

**Framework**: pytest with fixtures

### 10.3 Smoke Tests (Current)

**Coverage**:
- Health endpoint returns 200
- SQLi exploit triggers LEAK_MARKER
- Oracle detects exploit success

**Status**: COMPLETED

## 11. Future Enhancements

### 11.1 Multi-Step Exploits

Support exploit chains requiring multiple HTTP requests:
- Login → Exploit
- CSRF token fetch → Exploit

### 11.2 Stateful Targets

Support targets with session state:
- User authentication
- Shopping cart state
- Multi-user scenarios

### 11.3 Advanced Oracle Rules

- Regex pattern matching
- JSON path queries
- Database state inspection
- Timing-based detection

### 11.4 Patch Quality Metrics

- Code complexity before/after
- Test coverage impact
- Performance impact
- Security score improvement

## 12. Design Decisions Log

### 12.1 Why Config-Driven Oracle?

**Decision**: Use YAML configuration for Oracle rules instead of hardcoded logic.

**Rationale**:
- Different vulnerability types need different detection logic
- Researchers need flexibility to experiment with rules
- Easier to extend to new vulnerability types
- Reproducibility: rules are part of config snapshot

**Tradeoffs**:
- More complex configuration
- Potential for misconfiguration
- Less type safety than code

### 12.2 Why Subprocess for Targets?

**Decision**: Run targets as subprocesses instead of in-process or threads.

**Rationale**:
- Process isolation for safety
- Clean resource cleanup
- Easier to capture stdout/stderr
- Matches production deployment model

**Tradeoffs**:
- Slower startup than threads
- More complex lifecycle management
- Platform-specific process handling

### 12.3 Why Separate Verdict and Evidence?

**Decision**: Oracle returns both verdict (boolean decision) and evidence (supporting data).

**Rationale**:
- Verdict for automated decision-making
- Evidence for human review and debugging
- Supports audit trail and reproducibility
- Enables confidence scoring in future

**Tradeoffs**:
- More complex return type
- Potential for verdict/evidence mismatch

### 12.4 Why Python 3.11+?

**Decision**: Require Python 3.11 or later.

**Rationale**:
- Modern type hints (X | Y syntax)
- Performance improvements
- Better error messages
- Consistent development environment

**Tradeoffs**:
- Excludes users on older Python versions
- Requires explicit version management (pyenv)
- Potential compatibility issues with some libraries

## 13. Open Questions

1. **LLM Prompt Engineering**: What prompt strategies work best for each agent?
2. **Exploit Validation**: How to validate LLM-generated exploits before execution?
3. **Patch Safety**: How to ensure LLM-generated patches don't introduce new vulnerabilities?
4. **Benchmark Fairness**: How to ensure fair comparison across LLM providers with different capabilities?
5. **Energy Attribution**: How to accurately attribute energy to remote LLM calls vs. local orchestration?
6. **Scaling**: How to scale to hundreds of benchmark runs efficiently?
