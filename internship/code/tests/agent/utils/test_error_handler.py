"""Tests for error handling utilities."""
import pytest
from src.staking_optimizer.agent.utils.error_handler import handle_tool_error, ErrorResponse


def test_handle_value_error():
    """Test handling of ValueError."""
    error = ValueError("Invalid amount")
    context = {"operation": "stake"}
    
    response = handle_tool_error(error, context)
    assert isinstance(response, ErrorResponse)
    assert response.error == "Invalid Input"
    assert "Invalid amount" in response.details["message"]
    assert response.details["context"] == context
    assert "check your input" in response.suggestion.lower()


def test_handle_key_error():
    """Test handling of KeyError."""
    error = KeyError("address")
    context = {"operation": "unstake"}
    
    response = handle_tool_error(error, context)
    assert isinstance(response, ErrorResponse)
    assert response.error == "Not Found"
    assert "address" in response.details["message"]
    assert response.details["context"] == context
    assert "not found" in response.suggestion.lower()


def test_handle_unknown_error():
    """Test handling of unknown error types."""
    error = Exception("Unexpected error")
    
    response = handle_tool_error(error)
    assert isinstance(response, ErrorResponse)
    assert response.error == "Internal Error"
    assert "Unexpected error" in response.details["message"]
    assert "try again later" in response.suggestion.lower()


def test_handle_error_without_context():
    """Test error handling without context."""
    error = ValueError("Test error")
    
    response = handle_tool_error(error)
    assert isinstance(response, ErrorResponse)
    assert response.details["context"] is None
