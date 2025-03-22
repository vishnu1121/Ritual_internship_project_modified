"""Response models for agent operations."""
from typing import Optional
from pydantic import BaseModel


class AgentResponse(BaseModel):
    """Response from agent operations."""
    success: bool
    message: str
    error: Optional[str] = None
