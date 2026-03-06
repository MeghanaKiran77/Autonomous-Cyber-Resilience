# Autonomous Cyber-Resilience

Benchmarking Multi-Agent LLM Frameworks for Zero-Day Application-Layer Vulnerability Discovery and Verified Patching with outcome-normalized sustainability metrics: **Energy-to-Exploit (EtE)** and **Energy-to-Patch (EtP)**, to quantify the carbon cost of autonomous cyber-resilience workflows.

## Architecture

```
Researcher Agent → Attacker Agent → Verification Oracle → Fixer Agent → Re-Verification → Metrics
```

## Requirements

- **Python 3.11** (enforced at runtime)
- See `requirements.txt` for dependencies

## Setup (macOS / pyenv)

If you don't have Python 3.11:

```bash
pyenv install 3.11
pyenv global 3.11.14   # or: pyenv shell 3.11
```

To make 3.11 the default for new shells: `pyenv global 3.11.14`.  
This repo includes `.python-version` so `python` uses 3.11 when you're in the project directory.

If `pip install` fails with SSL/cert errors (common on macOS - Python/OpenSSL certs not linked):

```bash
# Workaround: bypass cert verification for install only
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt

# Or try certifi fix first:
python -m pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org certifi
export SSL_CERT_FILE=$(python -c "import certifi; print(certifi.where())")
pip install -r requirements.txt
```

Or run the setup script:

```bash
chmod +x scripts/setup_dev.sh
./scripts/setup_dev.sh
```

**If SSL errors persist on macOS** (OSStatus -26276), try:
1. Run Python’s certificate installer: `"/Applications/Python 3.x/Install Certificates.command"` (if using python.org installer)
2. Or use Colab for runs (clone repo, install, execute CLI there)

## Usage

```bash
python -m runner.run_experiment --config configs/run.yaml
```

## Workflow

- **Development:** Cursor IDE
- **Version control:** GitHub
- **Execution:** Colab (clone repo, run CLI) — see [colab/README_COLAB.md](colab/README_COLAB.md)
- **Artifacts:** Google Drive (`runs/`, `datasets/`, `targets/`, `reports/`)

## License

Apache-2.0
