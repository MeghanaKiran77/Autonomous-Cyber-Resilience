# Tasks: Autonomous Cyber-Resilience System

## Phase 1: Foundation (COMPLETED)

### 1. Configuration System
- [x] 1.1 Create Pydantic schema for configuration validation
- [x] 1.2 Implement YAML configuration loader
- [x] 1.3 Create local configuration (run.yaml)
- [x] 1.4 Create Colab configuration (run_colab.yaml)
- [x] 1.5 Add OracleConfig with rule-based verification

### 2. Run Management
- [x] 2.1 Implement run folder creation with unique IDs
- [x] 2.2 Implement run ID generation and retrieval
- [x] 2.3 Configure structured logging with structlog
- [x] 2.4 Add file logging to run folder

### 3. Target Infrastructure
- [x] 3.1 Create Flask SQLi demo application
- [x] 3.2 Implement database initialization with LEAK_MARKER
- [x] 3.3 Add health endpoint for readiness checks
- [x] 3.4 Add vulnerable search endpoint
- [x] 3.5 Implement target process runner
- [x] 3.6 Add health check polling with timeout
- [x] 3.7 Capture target stdout/stderr to logs

### 4. Verification Oracle
- [x] 4.1 Implement config-driven rule engine
- [x] 4.2 Add status code verification rules
- [x] 4.3 Add content marker verification rules
- [x] 4.4 Generate structured verdict output
- [x] 4.5 Generate structured evidence output
- [x] 4.6 Add structured logging for Oracle decisions

### 5. Minimal Pipeline
- [x] 5.1 Create CLI entrypoint with Click
- [x] 5.2 Add Python 3.11+ version enforcement
- [x] 5.3 Implement recon step (probe endpoints)
- [x] 5.4 Implement exploit step with configurable payload
- [x] 5.5 Integrate Oracle verification
- [x] 5.6 Write all artifacts to run folder
- [x] 5.7 Add graceful target shutdown

### 6. Testing Infrastructure
- [x] 6.1 Configure pytest with test discovery
- [x] 6.2 Create test fixtures for Flask app
- [x] 6.3 Write smoke test for health endpoint
- [x] 6.4 Write smoke test for SQLi exploit
- [x] 6.5 Write smoke test for Oracle detection

### 7. Documentation
- [x] 7.1 Write comprehensive README
- [x] 7.2 Write PROJECT_OVERVIEW with status tracking
- [x] 7.3 Document Colab execution workflow
- [x] 7.4 Document setup and troubleshooting

## Phase 2: LLM Agent Integration (NOT STARTED)

### 8. LLM Client Abstraction
- [x] 8.1 Design LLM client interface
  - [x] 8.1.1 Define base LLMClient class
  - [x] 8.1.2 Define LLMResponse data structure
  - [x] 8.1.3 Define error handling strategy
- [x] 8.2 Implement OpenAI client
  - [x] 8.2.1 Add OpenAI API integration
  - [x] 8.2.2 Add retry logic with exponential backoff
  - [x] 8.2.3 Add cost tracking per call
  - [x] 8.2.4 Add latency measurement
- [ ] 8.3 Implement Claude client
  - [ ] 8.3.1 Add Anthropic API integration
  - [ ] 8.3.2 Add retry logic with exponential backoff
  - [ ] 8.3.3 Add cost tracking per call
  - [ ] 8.3.4 Add latency measurement
- [ ] 8.4 Implement DeepSeek client
  - [ ] 8.4.1 Add DeepSeek API integration
  - [ ] 8.4.2 Add retry logic with exponential backoff
  - [ ] 8.4.3 Add cost tracking per call
  - [ ] 8.4.4 Add latency measurement
- [x] 8.5 Add structured output parsing
  - [x] 8.5.1 Implement JSON schema validation
  - [x] 8.5.2 Add error handling for invalid responses
- [ ]* 8.6 Add response caching (optional)
- [ ] 8.7 Write unit tests for LLM clients

### 9. Researcher Agent
- [x] 9.1 Design Researcher Agent interface
  - [x] 9.1.1 Define input schema (target spec, recon data)
  - [x] 9.1.2 Define output schema (findings)
- [x] 9.2 Implement target analysis logic
  - [x] 9.2.1 Create prompt template for target analysis
  - [x] 9.2.2 Implement LLM call with structured output
  - [x] 9.2.3 Parse and validate findings
- [x] 9.3 Add SQLi detection prompts
- [ ] 9.4 Add IDOR detection prompts
- [ ] 9.5 Add XSS detection prompts
- [x] 9.6 Write findings to run folder (findings.json)
- [x] 9.7 Add structured logging for Researcher decisions
- [ ] 9.8 Write integration tests for Researcher Agent

### 10. Attacker Agent
- [x] 10.1 Design Attacker Agent interface
  - [x] 10.1.1 Define input schema (findings)
  - [x] 10.1.2 Define output schema (exploits)
- [x] 10.2 Implement exploit generation logic
  - [x] 10.2.1 Create prompt template for exploit generation
  - [x] 10.2.2 Implement LLM call with structured output
  - [x] 10.2.3 Parse and validate exploits
- [x] 10.3 Add SQLi exploit generation prompts
  - [x] 10.3.1 Add SQL domain knowledge to system prompt
  - [x] 10.3.2 Add LIKE query specific guidance
  - [x] 10.3.3 Implement iterative refinement with Oracle feedback
- [ ] 10.4 Add IDOR exploit generation prompts
- [ ] 10.5 Add XSS exploit generation prompts
- [x] 10.6 Write exploits to run folder (exploits.json)
- [x] 10.7 Add structured logging for Attacker decisions
- [ ] 10.8 Write integration tests for Attacker Agent

### 11. Fixer Agent
- [x] 11.1 Design Fixer Agent interface
  - [x] 11.1.1 Define input schema (verified exploit, target context)
  - [x] 11.1.2 Define output schema (patch)
- [x] 11.2 Implement patch generation logic
  - [x] 11.2.1 Create prompt template for patch generation
  - [x] 11.2.2 Implement LLM call with structured output
  - [x] 11.2.3 Parse and validate patch
- [x] 11.3 Add SQLi patch generation prompts
- [ ] 11.4 Add IDOR patch generation prompts
- [ ] 11.5 Add XSS patch generation prompts
- [x] 11.6 Write patch to run folder (patch.json, patched_code.py)
- [x] 11.7 Add structured logging for Fixer decisions
- [ ] 11.8 Write integration tests for Fixer Agent

### 12. Agent Pipeline Integration
- [x] 12.1 Integrate Researcher Agent into runner
- [x] 12.2 Integrate Attacker Agent into runner
- [x] 12.3 Integrate Fixer Agent into runner
- [x] 12.4 Add agent chaining logic (Researcher → Attacker → Fixer)
- [x] 12.5 Add error handling for agent failures
- [ ] 12.6 Write end-to-end integration tests

## Phase 3: Additional Targets (NOT STARTED)

### 13. IDOR Target
- [ ] 13.1 Design IDOR demo application
  - [ ] 13.1.1 Define multi-user resource model
  - [ ] 13.1.2 Define authorization logic (intentionally flawed)
- [ ] 13.2 Implement IDOR Flask application
  - [ ] 13.2.1 Create user database with multiple users
  - [ ] 13.2.2 Add resource endpoints with predictable IDs
  - [ ] 13.2.3 Add health endpoint
  - [ ] 13.2.4 Add intentional authorization bypass
- [ ] 13.3 Configure IDOR Oracle rules
  - [ ] 13.3.1 Define success markers for unauthorized access
  - [ ] 13.3.2 Define fail markers for proper authorization
- [ ] 13.4 Add IDOR target to target registry
- [ ] 13.5 Write smoke tests for IDOR target
- [ ] 13.6 Write smoke tests for IDOR Oracle

### 14. XSS Target
- [ ] 14.1 Design XSS demo application
  - [ ] 14.1.1 Define reflected XSS scenario
  - [ ] 14.1.2 Define XSS marker for detection
- [ ] 14.2 Implement XSS Flask application
  - [ ] 14.2.1 Create endpoint with reflected user input
  - [ ] 14.2.2 Add health endpoint
  - [ ] 14.2.3 Add intentional XSS vulnerability (no sanitization)
- [ ] 14.3 Configure XSS Oracle rules
  - [ ] 14.3.1 Define success markers for script injection
  - [ ] 14.3.2 Define fail markers for proper sanitization
- [ ] 14.4 Add XSS target to target registry
- [ ] 14.5 Write smoke tests for XSS target
- [ ] 14.6 Write smoke tests for XSS Oracle

### 15. Target Registry
- [ ] 15.1 Design target registry system
  - [ ] 15.1.1 Define registry data structure
  - [ ] 15.1.2 Define target metadata schema
- [ ] 15.2 Implement target registry
  - [ ] 15.2.1 Create registry.py module
  - [ ] 15.2.2 Add target enumeration logic
  - [ ] 15.2.3 Add target lookup by type/name
- [ ] 15.3 Register all targets (SQLi, IDOR, XSS)
- [ ] 15.4 Update runner to use target registry
- [ ] 15.5 Write unit tests for target registry

## Phase 4: Patch Verification (NOT STARTED)

### 16. Patch Oracle
- [ ] 16.1 Design Patch Oracle interface
  - [ ] 16.1.1 Define input schema (exploit, patch, target)
  - [ ] 16.1.2 Define output schema (suppressed, regression, evidence)
- [ ] 16.2 Implement exploit suppression verification
  - [ ] 16.2.1 Re-run original exploit against patched target
  - [ ] 16.2.2 Verify exploit now fails
  - [ ] 16.2.3 Generate suppression evidence
- [ ] 16.3 Implement regression verification
  - [ ] 16.3.1 Define benign test cases per target type
  - [ ] 16.3.2 Run benign tests against patched target
  - [ ] 16.3.3 Verify benign tests still pass
  - [ ] 16.3.4 Generate regression evidence
- [ ] 16.4 Write patch verification results to run folder
- [ ] 16.5 Add structured logging for Patch Oracle decisions
- [ ] 16.6 Write integration tests for Patch Oracle

### 17. Patch Application
- [ ] 17.1 Design patch application system
  - [ ] 17.1.1 Define patch format (diff, full file, etc.)
  - [ ] 17.1.2 Define patch application strategy
- [ ] 17.2 Implement patch application logic
  - [ ] 17.2.1 Parse patch from Fixer Agent output
  - [ ] 17.2.2 Apply patch to target source
  - [ ] 17.2.3 Restart target with patched code
- [ ] 17.3 Add error handling for patch application failures
- [ ] 17.4 Write patch application logs to run folder
- [ ] 17.5 Write integration tests for patch application

### 18. Re-Verification Workflow
- [ ] 18.1 Integrate Patch Oracle into runner
- [ ] 18.2 Add re-verification step after patch application
- [ ] 18.3 Add conditional logic (only verify if patch applied)
- [ ] 18.4 Write end-to-end tests for full pipeline with patching

## Phase 5: Sandbox Integration (NOT STARTED)

### 19. udocker Integration
- [ ] 19.1 Research udocker requirements and setup
- [ ] 19.2 Create Dockerfile for SQLi target
- [ ] 19.3 Create Dockerfile for IDOR target
- [ ] 19.4 Create Dockerfile for XSS target
- [ ] 19.5 Implement container lifecycle management
  - [ ] 19.5.1 Pull/build container image
  - [ ] 19.5.2 Start container with target app
  - [ ] 19.5.3 Wait for health check
  - [ ] 19.5.4 Stop and remove container
- [ ] 19.6 Add network isolation configuration
- [ ] 19.7 Add resource limits (CPU, memory)
- [ ] 19.8 Add execution timeout enforcement
- [ ] 19.9 Update target runner to use containers
- [ ] 19.10 Write integration tests for containerized targets

### 20. Security Hardening
- [ ] 20.1 Implement localhost-only network binding
- [ ] 20.2 Add resource exhaustion protection
- [ ] 20.3 Add audit logging for all target interactions
- [ ] 20.4 Document threat model and mitigations
- [ ] 20.5 Conduct security review of sandbox implementation

## Phase 6: Energy Metrics (NOT STARTED)

### 21. CodeCarbon Integration
- [ ] 21.1 Add codecarbon to requirements.txt
- [ ] 21.2 Research CodeCarbon API and usage patterns
- [ ] 21.3 Implement energy tracking wrapper
  - [ ] 21.3.1 Create context manager for energy tracking
  - [ ] 21.3.2 Add start/stop tracking methods
  - [ ] 21.3.3 Add energy data collection
- [ ] 21.4 Wrap Researcher Agent with energy tracking
- [ ] 21.5 Wrap Attacker Agent with energy tracking
- [ ] 21.6 Wrap Fixer Agent with energy tracking
- [ ] 21.7 Calculate Energy-to-Exploit (EtE) metric
- [ ] 21.8 Calculate Energy-to-Patch (EtP) metric
- [ ] 21.9 Write energy metrics to run folder
- [ ] 21.10 Write unit tests for energy tracking

### 22. Metrics Collection
- [ ] 22.1 Design metrics schema with Pydantic
  - [ ] 22.1.1 Define per-run metrics structure
  - [ ] 22.1.2 Define aggregate metrics structure
- [ ] 22.2 Implement metrics logger
  - [ ] 22.2.1 Collect success/failure per stage
  - [ ] 22.2.2 Collect timing per stage
  - [ ] 22.2.3 Collect LLM token usage
  - [ ] 22.2.4 Collect LLM cost
  - [ ] 22.2.5 Collect energy metrics (EtE, EtP)
- [ ] 22.3 Write metrics to run folder (metrics.json)
- [ ] 22.4 Add metrics validation before write
- [ ] 22.5 Write unit tests for metrics logger

### 23. Metrics Aggregation
- [ ] 23.1 Design aggregation logic
  - [ ] 23.1.1 Group by provider/model/target
  - [ ] 23.1.2 Calculate success rates
  - [ ] 23.1.3 Calculate average EtE/EtP
  - [ ] 23.1.4 Calculate cost efficiency
  - [ ] 23.1.5 Calculate energy efficiency
- [ ] 23.2 Implement aggregation script
- [ ] 23.3 Write aggregated metrics to reports/
- [ ] 23.4 Write unit tests for aggregation logic

## Phase 7: Benchmark Runner (NOT STARTED)

### 24. Batch Execution
- [ ] 24.1 Design benchmark configuration format
  - [ ] 24.1.1 Define provider/model matrix
  - [ ] 24.1.2 Define target list
  - [ ] 24.1.3 Define repetition count
- [ ] 24.2 Implement benchmark runner
  - [ ] 24.2.1 Load benchmark configuration
  - [ ] 24.2.2 Generate run configurations for all combinations
  - [ ] 24.2.3 Execute runs sequentially
  - [ ] 24.2.4 Collect results per run
- [ ] 24.3 Add progress reporting during batch execution
- [ ] 24.4 Add error handling for failed runs
- [ ] 24.5 Write benchmark metadata to reports/
- [ ] 24.6 Write integration tests for benchmark runner

### 25. Report Generation
- [ ] 25.1 Design report formats
  - [ ] 25.1.1 JSON format for raw data
  - [ ] 25.1.2 CSV format for spreadsheet analysis
  - [ ] 25.1.3 HTML format for visual inspection
- [ ] 25.2 Implement JSON report generator
  - [ ] 25.2.1 Collect all run metrics
  - [ ] 25.2.2 Write to benchmark_results.json
- [ ] 25.3 Implement CSV report generator
  - [ ] 25.3.1 Aggregate metrics per configuration
  - [ ] 25.3.2 Write to benchmark_summary.csv
- [ ] 25.4 Implement HTML report generator
  - [ ] 25.4.1 Create HTML template
  - [ ] 25.4.2 Add summary tables
  - [ ] 25.4.3 Add charts (optional)
  - [ ] 25.4.4 Write to benchmark_report.html
- [ ] 25.5 Write unit tests for report generators

### 26. Reproducibility
- [ ] 26.1 Add config snapshot to run folder
- [ ] 26.2 Add dependency version tracking
- [ ] 26.3 Add seeded randomness for LLM calls
- [ ] 26.4 Document reproducibility requirements
- [ ] 26.5 Write reproducibility validation tests

## Phase 8: Polish and Documentation (NOT STARTED)

### 27. Code Quality
- [ ] 27.1 Add type hints to all functions
- [ ] 27.2 Add docstrings to all public functions
- [ ] 27.3 Run linter (ruff or pylint) and fix issues
- [ ] 27.4 Run formatter (black) on all code
- [ ] 27.5 Add pre-commit hooks for linting/formatting

### 28. Documentation
- [ ] 28.1 Write architecture documentation
- [ ] 28.2 Write API documentation for all modules
- [ ] 28.3 Write user guide for running experiments
- [ ] 28.4 Write developer guide for extending system
- [ ] 28.5 Write troubleshooting guide
- [ ] 28.6 Add example benchmark results
- [ ] 28.7 Add example reports

### 29. Testing
- [ ] 29.1 Achieve 80%+ code coverage
- [ ] 29.2 Add property-based tests for Oracle rules
- [ ] 29.3 Add stress tests for batch execution
- [ ] 29.4 Add performance benchmarks
- [ ] 29.5 Document testing strategy

### 30. Deployment
- [ ] 30.1 Create requirements.txt with pinned versions
- [ ] 30.2 Create setup script for fresh environments
- [ ] 30.3 Test on clean Colab environment
- [ ] 30.4 Test on clean local environment
- [ ] 30.5 Write deployment documentation

## Optional Enhancements (FUTURE)

### 31. Advanced Features*
- [ ]* 31.1 Multi-step exploit chains
- [ ]* 31.2 Stateful target support
- [ ]* 31.3 Advanced Oracle rules (regex, JSON path)
- [ ]* 31.4 Patch quality metrics
- [ ]* 31.5 Interactive mode for manual review
- [ ]* 31.6 Web UI for experiment management
- [ ]* 31.7 Real-time monitoring dashboard
- [ ]* 31.8 Distributed execution support

## Notes

- Tasks marked with [x] are completed
- Tasks marked with [ ] are not started
- Tasks marked with [ ]* are optional enhancements
- Sub-tasks are indented under parent tasks
- Complete all sub-tasks before marking parent task complete
- Phases should generally be completed in order, but some parallelization is possible
