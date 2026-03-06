"""OpenAI LLM client implementation."""

import json
import time
from typing import Any

import structlog

from llm.client import LLMClient, LLMResponse
from llm.exceptions import (
    LLMError,
    LLMInvalidResponseError,
    LLMRateLimitError,
    LLMRefusalError,
    LLMTimeoutError,
)

log = structlog.get_logger()


class OpenAIClient(LLMClient):
    """
    OpenAI API client implementation.
    
    Also compatible with OpenAI-compatible APIs like:
    - Groq (https://groq.com)
    - OpenRouter (https://openrouter.ai)
    - Local models via LM Studio, etc.
    """

    # Pricing per 1K tokens (as of 2024)
    PRICING = {
        # OpenAI models
        "gpt-4": {"input": 0.03, "output": 0.06},
        "gpt-4-turbo": {"input": 0.01, "output": 0.03},
        "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002},
        # Groq models (FREE tier - 2026 benchmarks)
        "qwen-qwq-32b": {"input": 0.0, "output": 0.0},  # Researcher: Deep reasoning
        "qwen-3-32b": {"input": 0.0, "output": 0.0},  # Researcher: Alternative
        "llama-4-scout-17b-16e-instruct": {"input": 0.0, "output": 0.0},  # Attacker: Fast MoE
        "gpt-oss-120b": {"input": 0.0, "output": 0.0},  # Fixer: Code-heavy
        "gpt-oss-20b": {"input": 0.0, "output": 0.0},  # Fixer: Faster alternative
        "kimi-k2": {"input": 0.0, "output": 0.0},  # Multilingual
        "llama-3.3-70b": {"input": 0.0, "output": 0.0},  # General purpose
        # Legacy Groq models
        "llama-3.1-70b-versatile": {"input": 0.0, "output": 0.0},
        "llama-3.1-8b-instant": {"input": 0.0, "output": 0.0},
        "mixtral-8x7b-32768": {"input": 0.0, "output": 0.0},
    }

    def __init__(self, model: str, api_key: str, base_url: str | None = None, **kwargs):
        """
        Initialize OpenAI client.
        
        Args:
            model: Model identifier.
            api_key: API key for authentication.
            base_url: Optional base URL for OpenAI-compatible APIs (e.g., Groq).
            **kwargs: Additional arguments passed to parent.
        """
        super().__init__(provider="openai", model=model, api_key=api_key, **kwargs)
        self.base_url = base_url
        
        try:
            from openai import OpenAI
            
            self.client = OpenAI(
                api_key=api_key,
                base_url=base_url,
                timeout=self.timeout_seconds,
            )
            log.info("openai_client_initialized", model=model, base_url=base_url)
        except ImportError:
            raise LLMError(
                "OpenAI SDK not installed. Install with: pip install openai"
            )

    def call(
        self,
        prompt: str,
        system: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> LLMResponse:
        """
        Call OpenAI API with text prompt.

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
        log.info(
            "openai_call_start",
            model=self.model,
            prompt_length=len(prompt),
            temperature=temperature,
        )

        def _make_request():
            start_time = time.time()
            
            try:
                messages = []
                if system:
                    messages.append({"role": "system", "content": system})
                messages.append({"role": "user", "content": prompt})

                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )

                latency_ms = (time.time() - start_time) * 1000
                
                # Extract response data
                content = response.choices[0].message.content
                tokens_input = response.usage.prompt_tokens
                tokens_output = response.usage.completion_tokens
                cost = self._calculate_cost(tokens_input, tokens_output)

                log.info(
                    "openai_call_success",
                    model=self.model,
                    tokens_input=tokens_input,
                    tokens_output=tokens_output,
                    cost_usd=cost,
                    latency_ms=latency_ms,
                )

                return LLMResponse(
                    content=content,
                    model=self.model,
                    provider=self.provider,
                    tokens_input=tokens_input,
                    tokens_output=tokens_output,
                    cost_usd=cost,
                    latency_ms=latency_ms,
                    metadata={
                        "finish_reason": response.choices[0].finish_reason,
                        "response_id": response.id,
                    },
                )

            except Exception as e:
                error_str = str(e).lower()
                
                # Map OpenAI errors to our exceptions
                if "timeout" in error_str:
                    raise LLMTimeoutError(f"OpenAI API timeout: {e}")
                elif "rate" in error_str or "429" in error_str:
                    raise LLMRateLimitError(f"OpenAI rate limit exceeded: {e}")
                elif "refused" in error_str or "content_policy" in error_str:
                    raise LLMRefusalError(f"OpenAI refused request: {e}")
                else:
                    raise LLMError(f"OpenAI API error: {e}")

        # Use retry logic from parent class
        return self._retry_with_backoff(_make_request)

    def call_structured(
        self,
        prompt: str,
        schema: dict[str, Any],
        system: str | None = None,
        temperature: float = 0.7,
    ) -> dict[str, Any]:
        """
        Call OpenAI API and parse response as structured JSON.

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
        log.info("openai_call_structured", model=self.model, schema_keys=list(schema.keys()))

        # Add JSON formatting instruction to prompt
        json_prompt = f"{prompt}\n\nRespond with valid JSON only. No additional text or explanation."
        
        # Add JSON schema to system prompt if provided
        if system:
            system_with_schema = f"{system}\n\nYou must respond with JSON matching this schema: {json.dumps(schema)}"
        else:
            system_with_schema = f"You must respond with JSON matching this schema: {json.dumps(schema)}"

        response = self.call(
            prompt=json_prompt,
            system=system_with_schema,
            temperature=temperature,
            max_tokens=2048,
        )

        # Parse JSON response
        try:
            parsed = json.loads(response.content)
            log.info("openai_structured_success", parsed_keys=list(parsed.keys()))
            return parsed
        except json.JSONDecodeError as e:
            log.error("openai_json_parse_failed", content=response.content[:200], error=str(e))
            raise LLMInvalidResponseError(
                f"Failed to parse JSON response: {e}\nContent: {response.content[:200]}"
            )

    def _calculate_cost(self, tokens_input: int, tokens_output: int) -> float:
        """Calculate cost based on OpenAI pricing."""
        pricing = self.PRICING.get(self.model, self.PRICING["gpt-3.5-turbo"])
        cost_input = (tokens_input / 1000) * pricing["input"]
        cost_output = (tokens_output / 1000) * pricing["output"]
        return cost_input + cost_output
