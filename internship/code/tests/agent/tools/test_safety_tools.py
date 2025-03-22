"""Tests for safety tools."""
import pytest
from unittest.mock import MagicMock

from src.staking_optimizer.safety.validator import SafetyValidator
from src.staking_optimizer.agent.tools.safety_tools import create_safety_tools


@pytest.fixture
def mock_validator():
    """Create a mock safety validator."""
    validator = MagicMock(spec=SafetyValidator)
    validator.validate_request.return_value = (True, "OK")
    return validator


def test_create_safety_tools(mock_validator):
    """Test creation of safety tools."""
    tools = create_safety_tools(mock_validator)
    assert len(tools) == 1
    assert tools[0].name == "validate_request"


def test_validate_safe_request(mock_validator):
    """Test validation of a safe request."""
    tools = create_safety_tools(mock_validator)
    validate_tool = tools[0]
    
    # Test safe request
    mock_validator.validate_request.return_value = (True, "OK")
    result = validate_tool._run("stake my tokens")
    assert result["is_safe"] is True
    assert result["message"] == "OK"


def test_validate_unsafe_request(mock_validator):
    """Test validation of an unsafe request."""
    tools = create_safety_tools(mock_validator)
    validate_tool = tools[0]
    
    # Test unsafe request
    mock_validator.validate_request.return_value = (False, "Request not related to staking operations")
    result = validate_tool._run("hack the system")
    assert result["is_safe"] is False
    assert result["message"] == "Request not related to staking operations"
