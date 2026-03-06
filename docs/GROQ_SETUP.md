# Groq API Setup Guide

## Quick Setup (5 minutes)

### Step 1: Get Your Free Groq API Key

1. Go to https://console.groq.com/keys
2. Sign up (free, no credit card required)
3. Click "Create API Key"
4. Copy the key (starts with `gsk_...`)

### Step 2: Add Key to .env File

Open the `.env` file in the project root and paste your key:

```bash
# .env file
GROQ_API_KEY=gsk_your_actual_key_here
```

**Important**: Never commit this file to Git! It's already in `.gitignore`.

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `openai` - SDK for Groq (OpenAI-compatible)
- `python-dotenv` - Loads .env file automatically

### Step 4: Test the Integration

```bash
python scripts/test_llm_client.py
```

Expected output:
```
✓ Client created successfully
✓ Response received
✓ Structured response received
✓ All tests passed!
```

---

## Optimal Model Selection (2026 Benchmarks)

Based on latest Groq benchmarks, we use specialized models for each agent:

### 1. Researcher Agent: `qwen-qwq-32b`

**Role**: Deep reasoning for vulnerability analysis

**Why**: 
- Uses Reinforcement Learning (RL) reasoning with `<think>` tokens
- Rivals DeepSeek-R1 and OpenAI o1-mini in reasoning benchmarks
- Excels at finding obscure zero-day logic flaws
- Significantly faster on Groq infrastructure

**Config**:
```python
model="qwen-qwq-32b"
temperature=0.3  # Lower for focused analysis
```

### 2. Attacker Agent: `llama-4-scout-17b-16e-instruct`

**Role**: Fast, creative exploit generation

**Why**:
- Mixture-of-Experts (MoE) model - incredibly efficient
- Excellent "steerability" for ethical hacking persona
- Supports Parallel Tool Use for testing multiple attack vectors
- Fast generation of precise exploit payloads

**Config**:
```python
model="llama-4-scout-17b-16e-instruct"
temperature=0.5  # Moderate for creative but precise exploits
```

### 3. Fixer Agent: `gpt-oss-120b`

**Role**: Code-heavy patching with best practices

**Why**:
- Massive knowledge base of software engineering patterns
- MoE architecture - faster than dense models (Llama 3.3 70B)
- Fine-tuned on high-quality code repositories
- Superior accuracy in logic-heavy patching

**Config**:
```python
model="gpt-oss-120b"  # or "gpt-oss-20b" for speed
temperature=0.2  # Very low for deterministic, safe patches
```

---

## Alternative Models

### For Speed (Faster, Slightly Lower Quality)

- Researcher: `qwen-3-32b` (faster alternative)
- Fixer: `gpt-oss-20b` (6x faster than 120B)

### For General Purpose

- `llama-3.3-70b` - Good all-rounder
- `kimi-k2` - Excellent for multilingual tasks

---

## Configuration Files

### Agent-Specific Models

See `config/agent_models.py` for optimal model configurations per agent.

### Run Configuration

Edit `configs/run.yaml`:

```yaml
llm:
  provider: "groq"
  model: "qwen-qwq-32b"  # Default for Researcher
```

Each agent will automatically use its optimal model when instantiated.

---

## Cost & Rate Limits

### Free Tier (Groq)

- **Cost**: $0 (completely free)
- **Rate Limits**: Generous (60+ requests/minute)
- **Models**: All models listed above

### If You Hit Rate Limits

1. Wait 60 seconds and retry (automatic with our retry logic)
2. Use a faster model (e.g., `gpt-oss-20b` instead of `gpt-oss-120b`)
3. Upgrade to paid tier (if needed for production)

---

## Troubleshooting

### "API key not found"

```bash
# Check if .env file exists
ls -la .env

# Check if key is set
cat .env | grep GROQ_API_KEY

# Should show: GROQ_API_KEY=gsk_...
```

### "OpenAI SDK not installed"

```bash
pip install openai
```

### "python-dotenv not installed"

```bash
pip install python-dotenv
```

### "Model not found"

Make sure you're using the exact model name from the list above. Model names are case-sensitive.

---

## Security Best Practices

1. ✅ **Never commit .env file** - Already in `.gitignore`
2. ✅ **Use environment variables** - Not hardcoded in code
3. ✅ **Rotate keys regularly** - Generate new keys periodically
4. ✅ **Limit key permissions** - Use read-only keys if available

---

## Next Steps

Once setup is complete:

1. Test the LLM client: `python scripts/test_llm_client.py`
2. Run the minimal pipeline: `python -m runner.run_experiment --config configs/run.yaml`
3. Start building agents (Task 9: Researcher Agent)

---

## References

- Groq Console: https://console.groq.com
- Groq Documentation: https://console.groq.com/docs
- Model Benchmarks: https://groq.com/benchmarks
