"""Error handling utilities for the StakingOptimizer agent."""
import logging
from typing import Any, Dict, Optional

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class ErrorResponse(BaseModel):
    """Response for error cases."""
    error: str
    details: Optional[Dict[str, Any]] = None
    suggestion: Optional[str] = None


def handle_tool_error(error: Exception, context: Optional[Dict[str, Any]] = None) -> ErrorResponse:
    """Handle errors from tool execution.
    
    Args:
        error: The exception that occurred
        context: Optional context about the error
        
    Returns:
        Formatted error response with suggestions
    """
    error_type = type(error).__name__
    error_msg = str(error)
    
    # Log the error
    logger.error(f"Tool error: {error_type} - {error_msg}", exc_info=True)
    
    # Handle specific error types
    if isinstance(error, ValueError):
        return ErrorResponse(
            error="Invalid Input",
            details={"message": error_msg, "context": context},
            suggestion="Please check your input values and try again"
        )
    elif isinstance(error, KeyError):
        return ErrorResponse(
            error="Not Found",
            details={"message": error_msg, "context": context},
            suggestion="The requested resource was not found"
        )
    else:
        return ErrorResponse(
            error="Internal Error",
            details={"message": error_msg, "context": context},
            suggestion="An unexpected error occurred. Please try again later"
        )
