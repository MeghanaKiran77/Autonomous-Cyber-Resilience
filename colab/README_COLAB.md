# Colab Execution Guide

Run the Autonomous Cyber-Resilience experiment in Google Colab. No Colab-specific code in core modules.

---

## Cell 1: Mount Drive

```python
from google.colab import drive
drive.mount('/content/drive')
```

---

## Cell 2: Clone Repo

```python
!rm -rf Autonomous-Cyber-Resilience  # optional: fresh clone
!git clone https://github.com/MeghanaKiran77/Autonomous-Cyber-Resilience.git
%cd Autonomous-Cyber-Resilience
```

---

## Cell 3: Install Dependencies

```python
!pip install -r requirements.txt
```

---

## Cell 4: Set Groq API Key

**IMPORTANT**: Set your Groq API key as an environment variable (never commit to Git!)

```python
import os

# Option 1: Set directly (for testing)
os.environ['GROQ_API_KEY'] = 'gsk_your_actual_key_here'

# Option 2: Use Colab Secrets (recommended)
# 1. Click the key icon in left sidebar
# 2. Add secret: GROQ_API_KEY = your-key
# 3. Then uncomment:
# from google.colab import userdata
# os.environ['GROQ_API_KEY'] = userdata.get('GROQ_API_KEY')
```

Get your free Groq API key at: https://console.groq.com/keys

---

## Cell 5: Test LLM Integration (Optional)

```python
!python scripts/test_llm_client.py
```

Expected output:
```
✓ Client created successfully
✓ Response received
✓ Structured response received
✓ All tests passed!
```

---

## Cell 6: Use Colab Config

The repo includes `configs/run_colab.yaml` with `drive_root` already set:

```python
# Verify config
!grep drive_root configs/run_colab.yaml
```

---

## Cell 7: Run Experiment

```python
!python -m runner.run_experiment --config configs/run_colab.yaml
```

---

## Cell 8: Show Run Folder and Artifacts

```python
!python scripts/print_latest_run.py --drive-root /content/drive/MyDrive/AgenticSecurity
```

---

## Inspect Specific Run

```python
# List all runs
!ls -la /content/drive/MyDrive/AgenticSecurity/runs/

# View specific run artifacts
!ls -la /content/drive/MyDrive/AgenticSecurity/runs/<run_id>/
```

---

## Troubleshooting

### "API key not found"

Make sure you set `GROQ_API_KEY` in Cell 4.

### "OpenAI SDK not installed"

Run: `!pip install openai`

### "Module not found"

Make sure you're in the project directory: `%cd Autonomous-Cyber-Resilience`
