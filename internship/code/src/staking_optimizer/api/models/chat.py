"""Chat API models.

This module defines the request and response models for the chat endpoint.
"""

from datetime import datetime
from typing import Dict, Optional, Any
from pydantic import BaseModel, Field, field_validator

class ChatMessage(BaseModel):
    """A chat message from either the user or assistant.
    
    Attributes:
        role: Either 'user' or 'assistant'
        content: The message content
        timestamp: When the message was created
        action: Optional action taken by the agent
    """
    role: str = Field(..., pattern="^(user|assistant)$", description="Either 'user' or 'assistant'")
    content: str = Field(..., description="The message content")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When the message was created")
    action: Optional[Dict[str, Any]] = Field(None, description="Optional action taken by the agent")

    @field_validator("content")
    def validate_content(cls, v: str) -> str:
        """Validate message length."""
        if not v.strip():
            raise ValueError("Message cannot be empty")
        if len(v) > 1000:
            raise ValueError("Message too long (max 1000 characters)")
        return v

class ChatRequest(BaseModel):
    """Chat request model.
    
    Attributes:
        message: User's chat message
    """
    message: str = Field(
        ...,
        description="User's chat message"
    )
    
    @field_validator("message")
    def validate_message(cls, v: str) -> str:
        """Validate message length."""
        if not v.strip():
            raise ValueError("Message cannot be empty")
        if len(v) > 1000:
            raise ValueError("Message too long (max 1000 characters)")
        return v

class ChatResponse(BaseModel):
    """Chat response model.
    
    Attributes:
        success: Whether the request was successful
        message: Response message
        error: Optional error message
    """
    success: bool = Field(..., description="Whether the request was successful")
    message: str = Field(..., description="Response message")
    error: Optional[str] = Field(None, description="Optional error message")
