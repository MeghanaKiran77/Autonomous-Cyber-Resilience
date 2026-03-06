"""
LLM client abstraction for multi-provider support.

Provides unified interface for OpenAI, Claude, and DeepSeek with:
- Retry logic with exponential backoff
- Cost and latency tracking
- Structured output parsing
- Response caching (optional)
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

import structlog

from llm.exceptions import LLMError

log = structlog.get_logger()


@dataclass
class LLMResponse:
    """
    Structured response from LLM API call.

    Attributes:
        content: The generated text content.
        model: Model identifier used for generation.
        provider: Provider name (openai, claude, deepseek).
        tokens_input: Number of input tokens.
        tokens_output: Number of output tokens.
        cost_usd: Estimated cost in USD.
        latency_ms: Response latency in milliseconds.
        metadata: Additional provider-specific metadata.
    """

    content: str
    model: str
    provider: str
    tokens_input: int
    tokens_output: int
    cost_usd: float
    latency_ms: float
    metadata: dict[str, Any] | None = None


class LLMClient(ABC):
    """
    Abstract base class for LLM clients.

    Provides unified interface for multiple LLM providers with:
    - Standard call() method for text generation
    - Structured output parsing via call_structured()
    - Automatic retry logic with exponential backoff
    - Cost and latency tracking
    """

    def __init__(
        self,
        provider: str,
        model: str,
        api_key: str,
        max_retries: int = 3,
        timeout_seconds: float = 60.0,
    ):
        """
        Initialize LLM client.

        Args:
            provider: Provider name (openai, claude, deepseek).
            model: Model identifier.
            api_key: API key for authentication.
            max_retries: Maximum number of retry attempts.
            timeout_seconds: Request timeout in seconds.
        """
        self.provider = provider
        self.model = model
        self.api_key = api_key
        self.max_retries = max_retries
        self.timeout_seconds = timeout_seconds
        log.info(
            "llm_client_initialized",
            provider=provider,
            model=model,
            max_retries=max_retries,
        )

    @abstractmethod
    def call(
        self,
        prompt: str,
        system: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> LLMResponse:
        """
        Call LLM API with text prompt.

        Args:
            prompt: User prompt text.
            system: Optional system prompt.
            temperature: Sampling temperature (0.0-1.0).
            max_tokens: Maximum tokens to generate.

        Returns:
            LLMResponse with generated content and metadata.

        Raises:
            LLMError: On API errors.
            LLMTimeoutError: On timeout.
            LLMRateLimitError: On rate limit exceeded.
        """
        pass

    @abstractmethod
    def call_structured(
        self,
        prompt: str,
        schema: dict[str, Any],
        system: str | None = None,
        temperature: float = 0.7,
    ) -> dict[str, Any]:
        """
        Call LLM API and parse response as structured JSON.

        Args:
            prompt: User prompt text.
            schema: JSON schema for expected response structure.
            system: Optional system prompt.
            temperature: Sampling temperature (0.0-1.0).

        Returns:
            Parsed JSON object matching schema.

        Raises:
            LLMError: On API errors.
            LLMInvalidResponseError: If response doesn't match schema.
        """
        pass

    @abstractmethod
    def _calculate_cost(self, tokens_input: int, tokens_output: int) -> float:
        """
        Calculate cost in USD for token usage.

        Args:
            tokens_input: Number of input tokens.
            tokens_output: Number of output tokens.

        Returns:
            Estimated cost in USD.
        """
        pass

    def _retry_with_backoff(self, func, *args, **kwargs):
        """
        Execute function with exponential backoff retry logic.

        Args:
            func: Function to execute.
            *args: Positional arguments for func.
            **kwargs: Keyword arguments for func.

        Returns:
            Function result.

        Raises:
            LLMError: If all retries exhausted.
        """
        import time

        from llm.exceptions import LLMRateLimitError, LLMTimeoutError

        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)
            except (LLMTimeoutError, LLMRateLimitError) as e:
                if attempt == self.max_retries - 1:
                    log.error(
                        "llm_retry_exhausted",
                        provider=self.provider,
                        model=self.model,
                        attempts=attempt + 1,
                        error=str(e),
                    )
                    raise
                backoff = 2**attempt
                log.warning(
                    "llm_retry_backoff",
                    provider=self.provider,
                    model=self.model,
                    attempt=attempt + 1,
                    backoff_seconds=backoff,
                    error=str(e),
                )
                time.sleep(backoff)
            except LLMError:
                # Non-retryable errors
                raise
