"""Tests for the chat endpoint.

This module contains tests for the chat endpoint, including input validation,
error handling, and integration with the StakingOptimizer agent.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

from staking_optimizer.api.main import app, get_chat_service
from staking_optimizer.api.core.errors import ValidationError, APIError
from staking_optimizer.blockchain import MockBlockchainState
from staking_optimizer.api.models.chat import ChatResponse
from tests.mocks.agent import MockStakingOptimizerAgent

# Test headers to simulate proper host
TEST_HEADERS = {
    "host": "test.example.com",
    "content-type": "application/json"
}

@pytest.fixture
def mock_agent():
    """Create a mock agent."""
    with patch("staking_optimizer.api.services.chat.StakingOptimizerAgent", MockStakingOptimizerAgent):
        yield

@pytest.fixture
def client(mock_agent):
    """Create a test client with mocked agent."""
    # Override allowed hosts for testing
    app.state.testing = True
    return TestClient(app, base_url="http://test.example.com")

def test_chat_empty_message(client):
    """Test that empty messages are rejected."""
    response = client.post(
        "/api/v1/chat",
        json={"message": ""},
        headers=TEST_HEADERS
    )
    assert response.status_code == 422  # FastAPI's default validation error code
    data = response.json()
    assert "detail" in data  # FastAPI validation error format
    assert any("empty" in str(error).lower() for error in data["detail"])

def test_chat_message_too_long(client):
    """Test that overly long messages are rejected."""
    response = client.post(
        "/api/v1/chat",
        json={"message": "x" * 1001},  # Over 1000 char limit
        headers=TEST_HEADERS
    )
    assert response.status_code == 422  # FastAPI's default validation error code
    data = response.json()
    assert "detail" in data  # FastAPI validation error format
    assert any("too long" in str(error).lower() for error in data["detail"])

@pytest.mark.asyncio
async def test_chat_success(client):
    """Test successful chat interaction."""
    # Send request
    response = client.post(
        "/api/v1/chat",
        json={"message": "I want to stake 1 ETH"},
        headers=TEST_HEADERS
    )
    
    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert data["success"]
    assert "message" in data
