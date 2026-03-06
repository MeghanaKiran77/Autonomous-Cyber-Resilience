"""Factory for creating LLM clients based on provider configuration."""

import os
from pathlib import Path

import structlog

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    
    # Look for .env in project root
    env_path = Path(__file__).resolve().parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    # python-dotenv not installed, rely on system environment variables
    pass

from config.schema import LLMConfig
from llm.client import LLMClient

log = structlog.get_logger()


def create_llm_client(config: LLMConfig) -> LLMClient:
    """
    Create LLM client based on configuration.

    Args:
        config: LLM configuration from RunConfig.

    Returns:
        Initialized LLM client for specified provider.

    Raises:
        ValueError: If provider is not supported or API key is missing.
    """
    provider = config.provider.lower()
    model = config.model

    # Get API key from environment
    api_key_env_map = {
        "openai": "OPENAI_API_KEY",
        "groq": "GROQ_API_KEY",
        "claude": "ANTHROPIC_API_KEY",
        "deepseek": "DEEPSEEK_API_KEY",
    }

    if provider not in api_key_env_map:
        raise ValueError(
            f"Unsupported provider: {provider}. "
            f"Supported: {list(api_key_env_map.keys())}"
        )

    env_var = api_key_env_map[provider]
    api_key = os.environ.get(env_var)

    if not api_key:
        raise ValueError(
            f"API key not found. Set environment variable: {env_var}\n"
            f"Example: export {env_var}=your-api-key-here"
        )

    # Import provider-specific client
    if provider == "openai":
        from llm.providers.openai_client import OpenAIClient

        client = OpenAIClient(model=model, api_key=api_key)
    elif provider == "groq":
        from llm.providers.openai_client import OpenAIClient

        # Groq uses OpenAI-compatible API
        client = OpenAIClient(
            model=model,
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1"
        )
        client.provider = "groq"  # Override provider name
    elif provider == "claude":
        from llm.providers.claude_client import ClaudeClient

        client = ClaudeClient(model=model, api_key=api_key)
    elif provider == "deepseek":
        from llm.providers.deepseek_client import DeepSeekClient

        client = DeepSeekClient(model=model, api_key=api_key)

    log.info("llm_client_created", provider=provider, model=model)
    return client
