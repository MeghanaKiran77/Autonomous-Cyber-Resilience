# Experimental Results

This folder contains results from benchmark runs for documentation and paper writing.

## Structure

```
results/
├── runs/              # Individual run artifacts
│   ├── run_001/       # First experimental run
│   │   ├── findings.json
│   │   ├── exploits.json
│   │   ├── oracle_verdict.json
│   │   ├── metrics.json
│   │   └── run.log
│   └── run_002/       # Second experimental run
│       └── ...
├── benchmarks/        # Aggregated benchmark results
│   ├── sqli_benchmark.json
│   └── model_comparison.csv
└── paper/             # Processed data for paper
    ├── figures/       # Generated charts and graphs
    ├── tables/        # LaTeX/CSV tables
    └── raw_data/      # Raw data for analysis
```

## Naming Convention

Run folders use format: `run_XXX_YYYY-MM-DD_description`

Example: `run_001_2026-03-06_sqli_llama33_baseline`

## What to Save

For each experimental run, save:
1. **findings.json** - Researcher Agent output
2. **exploits.json** - Attacker Agent output (when implemented)
3. **oracle_verdict.json** - Exploit verification results
4. **oracle_evidence.json** - Supporting evidence
5. **metrics.json** - Performance metrics (tokens, cost, latency, EtE)
6. **run.log** - Complete execution log
7. **config.yaml** - Configuration used for this run

## Analysis Scripts

Add Python scripts here to:
- Aggregate results across runs
- Generate comparison tables
- Create visualizations
- Calculate statistics (success rate, avg cost, avg latency)

## Paper Sections

Results will support:
- **Methodology**: Configuration and setup
- **Results**: Success rates, performance metrics
- **Discussion**: Model comparison, EtE/EtP analysis
- **Limitations**: Edge cases and failures
