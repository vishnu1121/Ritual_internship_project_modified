"""Error classes for the API.

This module defines custom error classes used by the API.
"""

from fastapi import HTTPException

class ValidationError(HTTPException):
    """Raised when request validation fails."""
    def __init__(self, message: str):
        super().__init__(status_code=400, detail=message)

class APIError(HTTPException):
    """Raised when there's an error processing the request."""
    def __init__(self, message: str):
        super().__init__(status_code=500, detail=message)

class NotFoundError(HTTPException):
    """Raised when a requested resource is not found."""
    def __init__(self, message: str):
        super().__init__(status_code=404, detail=message)

class SessionError(HTTPException):
    """Raised when there are session-related errors."""
    def __init__(self, message: str):
        super().__init__(status_code=400, detail=message)
