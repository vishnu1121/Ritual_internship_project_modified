"""Tests for the StakingOptimizer agent."""
import os
import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path
import logging
from dotenv import load_dotenv

from src.staking_optimizer.agent.base import StakingOptimizerAgent, AgentState
from src.staking_optimizer.blockchain.mock_contract import MockStakingContract
from src.staking_optimizer.blockchain.mock_state import MockBlockchainState
from langchain_ritual_toolkit import RitualToolkit
from langchain_ritual_toolkit.mock import MockRitualAPI
from langchain_openai import ChatOpenAI

# Configure logging to show LLM interactions
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG for maximum verbosity
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Enable verbose logging for langchain
langchain_logger = logging.getLogger("langchain")
langchain_logger.setLevel(logging.DEBUG)

# Enable verbose logging for OpenAI
openai_logger = logging.getLogger("openai")
openai_logger.setLevel(logging.DEBUG)

# Test private key (32 bytes in hex)
TEST_PRIVATE_KEY = "0x" + "1" * 64

@pytest.fixture(scope="session", autouse=True)
def load_env():
    """Load environment variables before running tests."""
    load_dotenv()
    if not os.getenv("OPENAI_API_KEY"):
        pytest.skip("OPENAI_API_KEY not found in environment")


@pytest.fixture
def mock_env():
    """Mock environment variables."""
    with patch.dict(os.environ, {
        "RITUAL_PRIVATE_KEY": "test_key",
        "RITUAL_RPC_URL": "test_url",
        "RITUAL_CONFIG_PATH": "test_path"
    }, clear=False):  # Don't clear existing env vars to keep API keys
        yield


@pytest.fixture
def mock_toolkit():
    """Create a mock RitualToolkit."""
    toolkit = MagicMock(spec=RitualToolkit)
    return toolkit

@pytest.fixture
def blockchain():
    """Create a mock blockchain state."""
    return MockBlockchainState()

@pytest.fixture
def contract(blockchain):
    """Create a mock staking contract."""
    return MockStakingContract(blockchain)

    
@pytest.fixture
def agent(load_env, mock_env, mock_toolkit, blockchain, contract)-> StakingOptimizerAgent:
    """Create a StakingOptimizerAgent instance."""
    agent = StakingOptimizerAgent(
        private_key=TEST_PRIVATE_KEY,
        rpc_url="test_url",
        config_path="test_path",
        mock_blockchain=blockchain,
        mock_contract=contract
    )
    return agent


@pytest.mark.asyncio
async def test_agent_initialization(agent):
    """Test agent initialization.
    
    This test verifies that:
    1. The LLM is configured with correct model and temperature
    2. The toolkit is properly configured with mock blockchain and contract
    3. The agent has all required tools
    4. Core components are properly initialized
    """
    # Verify LLM configuration
    assert isinstance(agent.llm, ChatOpenAI)
    assert agent.llm.model_name == "openai/gpt-4o-2024-11-20"
    assert agent.llm.temperature == 0.7

    # Verify toolkit configuration
    assert isinstance(agent.toolkit, RitualToolkit)
    assert isinstance(agent.toolkit.api, MockRitualAPI)
    assert agent.toolkit.api.blockchain is not None
    assert agent.toolkit.api.contract is not None

    # Verify required tools are present
    expected_tools = {
        'stake_tokens', 'execute_compound', 'claim_rewards',
        'GetStakingAPR', 'view_staking_position', 'unstake_tokens'
    }
    actual_tools = {tool.name for tool in agent.tools}
    assert expected_tools.issubset(actual_tools), f"Missing tools. Expected: {expected_tools}, Got: {actual_tools}"

    # Verify core components
    assert agent.validator is not None, "Safety validator not initialized"
    assert agent.operations is not None, "Staking operations not initialized"
    assert agent.command_parser is not None, "Command parser not initialized"
    assert agent.agent_executor is not None, "Agent executor not initialized"


@pytest.mark.asyncio
async def test_process_valid_request(agent):
    """Test processing a valid request for the current APR.
    
    This test verifies that:
    1. The agent can handle a simple APR query
    2. The response contains the default 5% APR formatted correctly
    3. The APR is formatted with one decimal place
    """
    logger = logging.getLogger(__name__)
    logger.info("Starting test_process_valid_request")

    state = AgentState(
        messages=[{
            "role": "user",
            "content": "What is the current APR?"  # Simplified query
        }],
        thread_id="test_thread"
    )

    logger.info("Invoking agent with APR query")
    result = await agent.invoke(state)
    logger.info(f"Agent response: {result.output}")

    # Verify the response
    assert result.output is not None
    assert isinstance(result.output, str)

    # Check for APR value with some flexibility in the decimal places
    response_lower = result.output.lower()
    print(f"response_lower: {result}")

    assert any(apr in response_lower for apr in ["5.0%", "5.00%"]), "Expected APR value (5%) not found in response"


@pytest.mark.asyncio
async def test_process_invalid_request(agent):
    """Test processing an invalid request."""
    mock_reason = "Request is unsafe"
    with patch.object(agent.validator, "validate_request", return_value=(False, mock_reason)), \
         patch.object(agent.validator, "get_last_error_message", return_value=mock_reason):
        state = AgentState(messages=[{"content": "test"}], thread_id="test")
        result = await agent.invoke(state)
        assert result.output == mock_reason


@pytest.mark.asyncio
async def test_process_request_error(agent):
    """Test error handling in request processing."""
    # Mock the validator to allow the request
    mock_validator = MagicMock()
    mock_validator.validate_request.return_value = True
    agent.validator = mock_validator
    
    # Mock the agent executor to raise an error
    mock_executor = MagicMock()
    mock_executor.invoke.side_effect = Exception("Test error")
    agent.agent_executor = mock_executor
    
    state = AgentState(messages=[{"content": "Test request"}], thread_id="test")
    result = await agent.invoke(state)
    assert "Error processing request" in result.output
