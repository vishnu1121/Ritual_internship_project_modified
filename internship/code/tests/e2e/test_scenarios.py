"""End-to-end tests for StakingOptimizer."""
import os
import logging
from decimal import Decimal
from typing import Generator

import pytest
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from src.staking_optimizer.agent.base import StakingOptimizerAgent, AgentResponse
from src.staking_optimizer.agent.tools import get_staking_tools
from src.staking_optimizer.blockchain.mock_state import MockBlockchainState
from src.staking_optimizer.blockchain.mock_contract import MockStakingContract
from src.staking_optimizer.autocompound.strategy import ThresholdStrategy
from src.staking_optimizer.commands.intents import IntentRecognizer
from src.staking_optimizer.commands.parser import CommandParser
from src.staking_optimizer.safety.validator import SafetyValidator

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
def intent_recognizer() -> IntentRecognizer:
    """Create intent recognizer."""
    return IntentRecognizer()


@pytest.fixture
def command_parser(intent_recognizer) -> CommandParser:
    """Create command parser."""
    return CommandParser()


@pytest.fixture
def compound_strategy() -> ThresholdStrategy:
    """Create compound strategy."""
    return ThresholdStrategy(
        min_reward_threshold=Decimal("0.1"),
        max_gas_price=Decimal("100"),
    )


@pytest.fixture
def agent(
    mock_blockchain,
    mock_contract,
    safety_validator,
    compound_strategy,
    intent_recognizer,
    command_parser,
) -> StakingOptimizerAgent:
    """Create StakingOptimizer agent."""
    agent = StakingOptimizerAgent(
        private_key="0x" + "1" * 64,  # 32 bytes hex string
        rpc_url="http://localhost:8545",
        config_path="test_config.json",
        model_name="openai/gpt-4o-2024-11-20",  # Use consistent model for all tests
        temperature=0.0,
        #intent_recognizer=intent_recognizer,
        command_parser=command_parser,
        safety_validator=safety_validator,
        compound_strategy=compound_strategy,
        mock_blockchain=mock_blockchain,
        mock_contract=mock_contract,
    )
    yield agent


@pytest.mark.asyncio
async def test_new_user_onboarding(agent, mock_blockchain, mock_contract):
    """Test complete new user onboarding flow."""
    # Initial setup - create user with 10 ETH
    user_address = "0x" + "2" * 40  # Valid Ethereum address
    mock_blockchain.create_account(user_address, float(10.0))
    
    # Step 1: User asks about staking
    request1 = "How can I start staking my ETH?"
    logger.info(f"\nStep 1 - Request: {request1}")
    response1 = await agent.handle_request(request1)
    logger.info(f"Step 1 - Response: {response1}")
    assert isinstance(response1, AgentResponse)
    assert response1.success
    assert "staking" in response1.message.lower()

    # Step 2: User stakes ETH
    stake_request = f"I want to stake 5 ETH from {user_address}"
    logger.info(f"\nStep 2 - Request: {stake_request}")
    response2 = await agent.handle_request(stake_request)
    logger.info(f"Step 2 - Response: {response2}")
    assert isinstance(response2, AgentResponse)
    assert response2.success
    assert any(word in response2.message.lower() for word in ["staked", "deposited", "success"])
    
    # Verify stake was successful
    stake_amount = mock_contract.get_stake(user_address)
    logger.info(f"Step 2 - Verification: Stake amount = {stake_amount}")
    assert stake_amount == Decimal("5.0"), f"Expected stake of 5.0 ETH but got {stake_amount}"

    # Step 3: User checks rewards
    mock_blockchain.mine_block()  # Simulate time passing
    # Let rewards accumulate naturally based on stake amount and time
    mock_contract.add_rewards(user_address, Decimal("0.1"))  # Add 0.1 ETH in rewards
    
    reward_request = f"How much rewards have I earned for {user_address}?"
    logger.info(f"\nStep 3 - Request: {reward_request}")
    response3 = await agent.handle_request(reward_request)
    logger.info(f"Step 3 - Response: {response3}")
    assert isinstance(response3, AgentResponse)
    assert response3.success
    assert "0.100000 ETH" in response3.message


@pytest.mark.asyncio
async def test_active_user_management(agent, mock_blockchain, mock_contract):
    """Test active user stake management scenario."""
    # Setup
    user_address = "0x" + "3" * 40  # Valid Ethereum address
    mock_blockchain.create_account(user_address, float(10.0))
    
    # Test 1: Initial stake
    stake_request = f"I want to stake 5 ETH from {user_address}"
    response1 = await agent.handle_request(stake_request)
    assert isinstance(response1, AgentResponse)
    assert response1.success
    assert any(word in response1.message.lower() for word in ["staked", "deposited", "success"])
    
    # Verify stake
    stake_amount = mock_contract.get_stake(user_address)
    assert stake_amount == Decimal("5.0"), f"Expected stake of 5.0 ETH but got {stake_amount}"
    
    # Test 2: Check position
    position_request = f"Show me the staking position for {user_address}"
    response2 = await agent.handle_request(position_request)
    assert isinstance(response2, AgentResponse)
    assert response2.success
    assert "5.000000 ETH" in response2.message
    
    # Test 3: Partial unstake
    unstake_request = f"I want to unstake 2 ETH from {user_address}"
    response3 = await agent.handle_request(unstake_request)
    assert isinstance(response3, AgentResponse)
    assert response3.success
    assert any(word in response3.message.lower() for word in ["unstaked", "withdrawn", "success"])
    
    # Verify unstake
    new_stake = mock_contract.get_stake(user_address)
    assert new_stake == Decimal("3.0"), f"Expected remaining stake of 3.0 ETH but got {new_stake}"


@pytest.mark.asyncio
async def test_auto_compound_scenario(agent, mock_blockchain, mock_contract, compound_strategy):
    """Test automatic compounding based on strategy."""
    # Setup
    user_address = "0x" + "4" * 40  # Valid Ethereum address
    mock_blockchain.create_account(user_address, float(10.0))
    
    # Initial stake
    stake_request = f"I want to stake 5 ETH from {user_address}"
    response1 = await agent.handle_request(stake_request)
    assert isinstance(response1, AgentResponse)
    assert response1.success
    
    # Add some rewards
    mock_contract.add_rewards(user_address, Decimal("0.5"))  # Add 0.5 ETH in rewards
    
    # Test auto-compound decision
    compound_request = f"Should I compound my rewards now for {user_address}?"
    response2 = await agent.handle_request(compound_request)
    assert isinstance(response2, AgentResponse)
    assert response2.success
    assert "compound" in response2.message.lower()
    
    # Execute auto-compound
    compound_execution = f"Compound rewards for {user_address}"
    response3 = await agent.handle_request(compound_execution)
    assert isinstance(response3, AgentResponse)
    assert response3.success
    assert "success" in response3.message.lower()
    
    # Verify rewards were compounded
    new_stake = mock_contract.get_stake(user_address)
    assert new_stake > Decimal("5.0"), "Stake should have increased after compounding"


@pytest.mark.asyncio
async def test_error_recovery_scenario(agent, mock_blockchain, mock_contract):
    """Test system recovery from various error conditions."""
    # Setup
    user_address = "0x" + "5" * 40  # Valid Ethereum address
    mock_blockchain.create_account(user_address, float(1.0))  # Only 1 ETH
    
    # Test 1: Attempt to stake more than balance
    stake_request = f"Stake 2 ETH from {user_address}"  # Only has 1 ETH
    response1 = await agent.handle_request(stake_request)
    assert isinstance(response1, AgentResponse)
    assert not response1.success  # Should fail
    assert "insufficient" in response1.message.lower()
    
    # Test 2: Recovery - successful stake after error
    stake_request_2 = f"Stake 0.5 ETH from {user_address}"
    response2 = await agent.handle_request(stake_request_2)
    assert isinstance(response2, AgentResponse)
    assert response2.success
    assert "success" in response2.message.lower()


@pytest.mark.asyncio
async def test_performance_degradation_scenario(agent, mock_blockchain, mock_contract):
    """Test system behavior under degraded conditions."""
    # Setup
    user_address = "0x" + "6" * 40  # Valid Ethereum address
    mock_blockchain.create_account(user_address, float(10.0))
    mock_contract.stake(user_address, Decimal("5.0"))
    mock_contract.set_apr(Decimal("0.10"))  # Start with 10% APR
    
    # Test 1: Check APR under normal conditions
    apr_request = f"What is the current APR for {user_address}?"
    response1 = await agent.handle_request(apr_request)
    assert isinstance(response1, AgentResponse)
    assert response1.success
    assert "10.0%" in response1.message
    
    # Test 2: APR degradation
    mock_contract.set_apr(Decimal("0.05"))  # Reduce to 5% APR
    apr_request_2 = f"What is the current APR for {user_address}?"
    response2 = await agent.handle_request(apr_request_2)
    assert isinstance(response2, AgentResponse)
    assert response2.success
    assert "5.0%" in response2.message
    
    # Test 3: System recommendations for degraded conditions
    recommendation_request = f"What should I do about the reduced APR for {user_address}?"
    response3 = await agent.handle_request(recommendation_request)
    assert isinstance(response3, AgentResponse)
    assert response3.success
    
    # Verify response provides meaningful advice
    message = response3.message.lower()
    assert len(message.split()) > 10, "Response should provide meaningful advice about APR"
    
    # Test 4: Unstake due to low APR
    unstake_request = f"Unstake all from {user_address} due to low APR"
    response4 = await agent.handle_request(unstake_request)
    assert isinstance(response4, AgentResponse)
    assert response4.success
    assert any(word in response4.message.lower() for word in ["unstaked", "withdrawn", "success"])
    
    # Verify complete unstake
    final_stake = mock_contract.get_stake(user_address)
    assert final_stake == Decimal("0"), f"Expected final stake of 0 ETH but got {final_stake}"
