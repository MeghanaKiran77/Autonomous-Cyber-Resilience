# Setup Scripts

## `print_latest_run.py` – Show Latest Run Artifacts

```bash
python scripts/print_latest_run.py
# Or with Colab drive path:
python scripts/print_latest_run.py --drive-root /content/drive/MyDrive/AgenticSecurity
```

## `setup_dev.sh` – Fix SSL + Install (macOS/pyenv)

If `pip install` fails with `SSLCertVerificationError`:

1. Use Python 3.11:
   ```bash
   pyenv shell 3.11
   ```

2. Run the setup script:
   ```bash
   chmod +x scripts/setup_dev.sh
   ./scripts/setup_dev.sh
   ```

3. Or manually:
   ```bash
   python -m pip install --upgrade pip certifi
   export SSL_CERT_FILE=$(python -c "import certifi; print(certifi.where())")
   pip install -r requirements.txt
   ```

4. (Optional) Add to `~/.zshrc` so pip always uses certifi:
   ```bash
   export SSL_CERT_FILE=$(python3 -c "import certifi; print(certifi.where())" 2>/dev/null || true)
   ```
