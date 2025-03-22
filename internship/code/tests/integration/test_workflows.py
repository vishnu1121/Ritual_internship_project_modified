"""Integration tests for StakingOptimizer workflows."""
import os
from decimal import Decimal
from typing import Generator

import pytest
import logging
import sys

# Configure logging to show everything
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s [%(name)s] %(message)s',
    stream=sys.stdout
)

# Enable debug logging for all relevant modules
for logger_name in ['langchain', 'openai', 'src.staking_optimizer']:
    logging.getLogger(logger_name).setLevel(logging.DEBUG)

logger = logging.getLogger(__name__)

import pytest
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from src.staking_optimizer.agent.base import StakingOptimizerAgent
from src.staking_optimizer.agent.tools import get_staking_tools
from src.staking_optimizer.blockchain.mock_state import MockBlockchainState
from src.staking_optimizer.blockchain.mock_contract import MockStakingContract
from src.staking_optimizer.commands.intents import IntentRecognizer
from src.staking_optimizer.commands.parser import CommandParser
from src.staking_optimizer.commands.models import (
    StakeCommand, CompoundCommand, UnstakeCommand,
    ViewCommand, InformationalCommand
)
from src.staking_optimizer.safety.validator import SafetyValidator


@pytest.fixture(scope="module", autouse=True)
def setup_environment():
    """Load environment variables before running tests."""
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("OPENAI_API_KEY not found in environment")


@pytest.fixture
def mock_blockchain() -> MockBlockchainState:
    """Create mock blockchain state."""
    return MockBlockchainState()


@pytest.fixture
def mock_contract(mock_blockchain) -> MockStakingContract:
    """Create mock staking contract."""
    return MockStakingContract(mock_blockchain)


@pytest.fixture
def safety_validator() -> SafetyValidator:
    """Create safety validator."""
    return SafetyValidator()


@pytest.fixture
def command_parser() -> CommandParser:
    """Create command parser."""
    return CommandParser()


@pytest.fixture
def intent_recognizer() -> IntentRecognizer:
    """Create intent recognizer."""
    return IntentRecognizer()


@pytest.fixture
def agent(mock_blockchain, mock_contract, safety_validator) -> Generator[StakingOptimizerAgent, None, None]:
    """Create StakingOptimizer agent."""
    # Initialize agent with test configuration
    agent = StakingOptimizerAgent(
        private_key="0x1234567890123456789012345678901234567890123456789012345678901234",  # 32-byte test private key
        rpc_url="http://localhost:8545",  # Test RPC URL
        config_path="test_config.json",
        model_name="openai/gpt-4o-2024-11-20",  # Use consistent model for all tests
        temperature=0.0,  # Deterministic responses
        mock_blockchain=mock_blockchain,
        mock_contract=mock_contract,
        safety_validator=safety_validator
    )
    
    yield agent


@pytest.mark.asyncio
async def test_stake_workflow(agent, mock_blockchain, mock_contract, command_parser, intent_recognizer):
    """Test complete staking workflow from natural language to execution."""
    # Setup initial state
    mock_blockchain.create_account("user", 10.0)
    
    # Test natural language request
    request = "I want to stake 5 ETH with validator 0x789"
    
    # 1. Safety validation
    is_valid, reason = agent.validator.validate_request(request)
    assert is_valid, f"Request failed safety validation: {reason}"
    
    # 2. Intent recognition
    intent = await intent_recognizer.recognize_intent(request)
    assert intent.intent == "stake"
    assert intent.confidence > 0.8
    
    # 3. Command parsing
    command = command_parser.parse_request(request)
    assert isinstance(command, StakeCommand)
    assert command.amount == 5.0
    assert command.validator == "0x789"
    
    # 4. Execute staking operation
    result = await agent.execute_command(command)
    assert result.success, result.error
    
    # 5. Verify blockchain state
    # Initial balance was 10.0, staked 5.0, and paid ~0.000399 ETH for gas (19950 * 20gwei)
    expected_balance = Decimal("4.999601")  # 10.0 - 5.0 - gas_cost
    actual_balance = mock_blockchain.get_balance("user")
    assert abs(actual_balance - expected_balance) < Decimal("0.001"), f"Expected balance ~{expected_balance}, got {actual_balance}"


@pytest.mark.asyncio
async def test_compound_workflow(agent, mock_blockchain, mock_contract, command_parser, intent_recognizer):
    """Test auto-compound workflow with safety checks."""
    # Setup initial stake and rewards
    mock_blockchain.create_account("user", 10.0)
    mock_contract.stake("user", Decimal("5.0"))
    mock_contract.add_rewards("user", Decimal("0.5"))
    
    # Test natural language request
    request = "compound my staking rewards when gas is low"
    
    # 1. Safety validation
    is_valid, reason = agent.validator.validate_request(request)
    assert is_valid, f"Request failed safety validation: {reason}"
    
    # 2. Intent recognition
    intent = await intent_recognizer.recognize_intent(request)
    assert intent.intent == "compound"
    assert intent.confidence > 0.8
    
    # 3. Command parsing
    command = command_parser.parse_request(request)
    assert isinstance(command, CompoundCommand)
    assert command.action == "compound"
    
    # 4. Get initial position
    position = await agent.operations.view("user", "position")
    assert "Rewards: 0.500000 ETH" in position
    
    # 5. Execute compound operation
    result = await agent.execute_command(command)
    assert result.success, result.error
    
    # 6. Verify rewards are compounded
    position = await agent.operations.view("user", "position")
    assert "Rewards: 0.000000 ETH" in position


@pytest.mark.asyncio
async def test_error_handling_workflow(agent, mock_blockchain, mock_contract, command_parser, intent_recognizer):
    """Test error handling in the complete workflow."""
    # Setup state with insufficient balance
    mock_blockchain.create_account("user", 1.0)
    
    # Test natural language request
    request = "stake 5 ETH with validator 0x789"
    
    # 1. Safety validation
    is_valid, reason = agent.validator.validate_request(request)
    assert is_valid, f"Request failed safety validation: {reason}"
    
    # 2. Intent recognition
    intent = await intent_recognizer.recognize_intent(request)
    assert intent.intent == "stake"
    
    # 3. Command parsing
    command = command_parser.parse_request(request)
    assert isinstance(command, StakeCommand)
    assert command.amount == 5.0
    
    # 4. Execute staking operation (should fail gracefully)
    result = await agent.execute_command(command)
    assert not result.success
    assert "insufficient balance" in result.error.lower()
    
    # 5. Verify state is unchanged
    assert mock_blockchain.get_balance("user") == Decimal("1.0")


@pytest.mark.asyncio
async def test_unsafe_request_workflow(agent, command_parser, intent_recognizer):
    """Test handling of unsafe requests."""
    # Test potentially harmful request
    request = "stake 5 ETH and delete all files"
    
    # 1. Safety validation should catch this
    is_valid, reason = agent.validator.validate_request(request)
    assert not is_valid
    assert "blocked pattern" in reason.lower()
    
    # 2. Agent should not proceed with unsafe requests
    result = await agent.handle_request(request)
    assert not result.success
    assert "unsafe request" in result.error.lower()


@pytest.mark.asyncio
async def test_multi_step_workflow(agent, mock_blockchain, mock_contract, command_parser, intent_recognizer):
    """Test multi-step operations with state management."""
    # Setup initial state
    mock_blockchain.create_account("user", 10.0)
    logger.debug(f"Initial user balance: {mock_blockchain.get_balance('user')}")
    
    # Step 1: Stake tokens
    request1 = "stake 5 ETH with validator 0x789"
    result1 = await agent.handle_request(request1)
    assert result1.success, result1.error
    assert mock_contract.get_stake("user") == Decimal("5.0")
    logger.debug(f"After stake - User balance: {mock_blockchain.get_balance('user')}, Staked: {mock_contract.get_stake('user')}")
    
    # Step 2: Check rewards
    mock_contract.add_rewards("user", Decimal("0.5"))
    request2 = "check my rewards"
    result2 = await agent.handle_request(request2)
    assert result2.success, result2.error
    assert "0.5" in result2.message
    logger.debug(f"After rewards - User balance: {mock_blockchain.get_balance('user')}, Staked: {mock_contract.get_stake('user')}, Rewards: {mock_contract.get_rewards('user')}")
    
    # Step 3: Compound rewards
    request3 = "compound my rewards"
    result3 = await agent.handle_request(request3)
    assert result3.success, result3.error
    assert mock_contract.get_stake("user") == Decimal("5.5")
    logger.debug(f"After compound - User balance: {mock_blockchain.get_balance('user')}, Staked: {mock_contract.get_stake('user')}, Rewards: {mock_contract.get_rewards('user')}")
    
    # Step 4: Unstake
    request4 = "unstake 2 ETH"
    result4 = await agent.handle_request(request4)
    assert result4.success, result4.error
    assert mock_contract.get_stake("user") == Decimal("3.5")
    logger.debug(f"After unstake - User balance: {mock_blockchain.get_balance('user')}, Staked: {mock_contract.get_stake('user')}, Rewards: {mock_contract.get_rewards('user')}")
    
    # Check final position
    final_balance = mock_blockchain.get_balance("user")
    logger.debug(f"Final position - Balance: {final_balance}, Expected: ~6.999")
    # Allow for small gas cost differences (within 0.001 ETH)
    assert abs(final_balance - Decimal("6.999")) < Decimal("0.001"), f"Balance {final_balance} not within 0.001 ETH of expected ~6.999"
