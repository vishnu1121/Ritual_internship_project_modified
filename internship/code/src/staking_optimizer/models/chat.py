"""Models for chat API."""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class ChatResponse(BaseModel):
    """Response from chat API."""
    message: str = Field(..., description="Response message from the agent")
    action: Optional[Dict[str, Any]] = Field(None, description="Optional action returned by the agent")
