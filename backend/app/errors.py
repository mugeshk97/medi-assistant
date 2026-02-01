"""Custom exception classes for error handling."""

from typing import Optional


class MediAssistantError(Exception):
    """Base exception for all MediAssistant errors."""

    def __init__(self, message: str, details: Optional[dict] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class ThreadNotFoundError(MediAssistantError):
    """Raised when a thread is not found."""

    pass


class UnauthorizedError(MediAssistantError):
    """Raised when user is not authorized to access a resource."""

    pass


class ValidationError(MediAssistantError):
    """Raised when input validation fails."""

    pass


class DatabaseError(MediAssistantError):
    """Raised when a database operation fails."""

    pass


class AIServiceError(MediAssistantError):
    """Raised when the AI service (OpenAI) encounters an error."""

    pass


class RateLimitError(MediAssistantError):
    """Raised when rate limit is exceeded."""

    pass
