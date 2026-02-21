"""Pydantic models for request/response validation."""

from typing import List, Literal
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
import re


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""

    message: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="User message content",
    )
    thread_id: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Required unique thread identifier managed by the client.",
    )

    @field_validator("message")
    @classmethod
    def validate_message(cls, v: str) -> str:
        """Sanitize and validate message content."""
        # Remove potentially dangerous characters
        sanitized = re.sub(r"[<>]", "", v.strip())
        if not sanitized:
            raise ValueError("Message cannot be empty after sanitization")
        return sanitized


class Thread(BaseModel):
    """Thread model for listing user threads."""

    thread_id: str
    title: str
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        """Pydantic configuration."""

        json_encoders = {datetime: lambda v: v.isoformat()}


class Message(BaseModel):
    """Individual message model."""

    role: Literal["user", "assistant", "system"]
    content: str
    id: str | None = None


class ChatHistoryResponse(BaseModel):
    """Response model for chat history endpoint."""

    thread_id: str
    messages: List[Message]
