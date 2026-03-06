# LLM Client Setup Guide

## Quick Start with Groq (FREE)

Groq provides free, fast LLM API access - perfect for development!

### 1. Get Your API Key

1. Go to https://console.groq.com/keys
2. Sign up (free)
3. Create a new API key
4. Copy the key

### 2. Set Environment Variable

```bash
export GROQ_API_KEY=your-key-here
```

To make it permanent, add to your `~/.zshrc` or `~/.bashrc`:

```bash
echo 'export GROQ_API_KEY=your-key-here' >> ~/.zshrc
source ~/.zshrc
```

### 3. Install Dependencies

```bash
pip install openai
```

### 4. Test the Integration

```bash
python scripts/test_llm_client.py
```

You should see:
```
✓ Client created successfully
✓ Response received
✓ Structured response received
✓ All tests passed!
```

## Available Models

### Groq (Free)

- `llama-3.1-70b-versatile` - Best quality (default)
- `llama-3.1-8b-instant` - Fastest
- `mixtral-8x7b-32768` - Long context

### OpenAI (Paid)

Set `OPENAI_API_KEY` and update config:

```yaml
llm:
  provider: "openai"
  model: "gpt-3.5-turbo"  # Cheapest: ~$0.01/run
```

### Claude (Paid)

Set `ANTHROPIC_API_KEY` and update config:

```yaml
llm:
  provider: "claude"
  model: "claude-3-sonnet"  # Mid-tier: ~$0.04/run
```

## Configuration

Edit `configs/run.yaml`:

```yaml
llm:
  provider: "groq"  # groq | openai | claude | deepseek
  model: "llama-3.1-70b-versatile"
```

## Troubleshooting

### "API key not found"

Make sure you've exported the environment variable:

```bash
echo $GROQ_API_KEY  # Should print your key
```

### "OpenAI SDK not installed"

```bash
pip install openai
```

### "Rate limit exceeded"

Groq free tier has generous limits, but if you hit them:
- Wait a minute and retry
- Use a different model
- Sign up for paid tier

## Cost Tracking

The system automatically tracks:
- Tokens used (input/output)
- Estimated cost per call
- Total latency

Check `run.log` for detailed metrics.
