#!/usr/bin/env bash
# Fix SSL/cert issues and install dependencies (macOS/pyenv).
# Run from project root: ./scripts/setup_dev.sh

set -e

# Check Python version (requires 3.11+)
python3 -c 'import sys; sys.exit(0 if (sys.version_info.major, sys.version_info.minor) >= (3, 11) else 1)' || {
  echo "Error: Python 3.11+ required. Current: $(python3 --version 2>&1)"
  echo "Run: pyenv shell 3.11"
  exit 1
}

# Fix 1: upgrade pip and certifi
python3 -m pip install --upgrade pip certifi

# Fix 2: use certifi for SSL (pyenv)
export SSL_CERT_FILE=$(python3 -c "import certifi; print(certifi.where())")
export REQUESTS_CA_BUNDLE=$SSL_CERT_FILE

# Install project deps
pip install -r requirements.txt

echo "Done. Run: python -m runner.run_experiment --config configs/run.yaml"
