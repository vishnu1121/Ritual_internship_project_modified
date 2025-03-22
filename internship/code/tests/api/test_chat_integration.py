"""Integration tests for chat API."""

import logging
import pytest
from fastapi.testclient import TestClient

from staking_optimizer.api.main import app
from staking_optimizer.api.services.chat import ChatService
from staking_optimizer.blockchain import MockBlockchainState, MockStakingContract

# Set log level to DEBUG
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@pytest.fixture(scope="function")
def mock_blockchain() -> MockBlockchainState:
    """Create mock blockchain state."""
    return MockBlockchainState()

@pytest.fixture(scope="function")
def mock_contract(mock_blockchain) -> MockStakingContract:
    """Create mock staking contract."""
    return MockStakingContract(mock_blockchain)

@pytest.fixture(scope="function")
def test_client(mock_blockchain, mock_contract) -> TestClient:
    """Create test client with mock blockchain and contract."""
    # Initialize chat service with mocks
    chat_service = ChatService(mock_blockchain, mock_contract)
    app.dependency_overrides[ChatService] = lambda: chat_service
    
    # Create test client
    client = TestClient(app)
    yield client
    
    # Clean up
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_chat_about_staking(test_client):
    """Test chatting about staking operations."""
    response = test_client.post(
        "/api/v1/chat",
        json={"message": "Can you help me understand how to stake ETH?"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "success" in data
    assert data["success"] is True
    assert "message" in data
    assert "error" in data
    assert data["error"] is None
    # Check that the response contains relevant staking information
    assert any(keyword in data["message"].lower() for keyword in [
        "stake", "staking", "eth", "deposit", "lock", "rewards"
    ]), f"Response did not contain expected keywords: {data['message']}"

@pytest.mark.asyncio
async def test_chat_about_unstaking(test_client):
    """Test chatting about unstaking operations."""
    response = test_client.post(
        "/api/v1/chat",
        json={"message": "How do I unstake my ETH?"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "success" in data
    assert data["success"] is True
    assert "message" in data
    assert "error" in data
    assert data["error"] is None
    assert "unstaking" in data["message"].lower()

@pytest.mark.asyncio
async def test_chat_general_question(test_client):
    """Test chatting about general staking info."""
    response = test_client.post(
        "/api/v1/chat",
        json={"message": "What can you help me with?"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "success" in data
    assert "message" in data
    assert "error" in data
    assert any(keyword in data["message"].lower() for keyword in ["staking", "rewards", "apr"])

@pytest.mark.asyncio
async def test_chat_empty_message(test_client):
    """Test sending empty message."""
    response = test_client.post(
        "/api/v1/chat",
        json={"message": ""}
    )
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_chat_long_message(test_client):
    """Test sending very long message."""
    response = test_client.post(
        "/api/v1/chat",
        json={"message": "a" * 10000}
    )
    assert response.status_code == 422
