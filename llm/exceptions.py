"""LLM client exceptions."""


class LLMError(Exception):
    """Base exception for LLM client errors."""

    pass


class LLMTimeoutError(LLMError):
    """Raised when LLM API call times out."""

    pass


class LLMRateLimitError(LLMError):
    """Raised when LLM API rate limit is exceeded."""

    pass


class LLMInvalidResponseError(LLMError):
    """Raised when LLM returns invalid or unparseable response."""

    pass


class LLMRefusalError(LLMError):
    """Raised when LLM refuses to generate requested content."""

    pass
