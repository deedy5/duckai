class DuckAIException(Exception):
    """Base exception class for duckai."""


class RatelimitException(DuckAIException):
    """Raised for rate limit exceeded errors during API requests."""


class TimeoutException(DuckAIException):
    """Raised for timeout errors during API requests."""


class ConversationLimitException(DuckAIException):
    """Raised for conversation limit during API requests to AI endpoint."""
