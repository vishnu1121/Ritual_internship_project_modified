"""Tests for reward monitoring functionality."""

from datetime import datetime, timedelta
from decimal import Decimal

import pytest
from src.staking_optimizer.autocompound.monitor import RewardMonitor
from src.staking_optimizer.autocompound.strategy import ThresholdStrategy
from src.staking_optimizer.blockchain.mock_contract import MockStakingContract
from src.staking_optimizer.blockchain.mock_state import MockBlockchainState


@pytest.fixture
def test_address():
    """Test address for staking position."""
    return "0x123"


@pytest.fixture
def mock_blockchain():
    """Create mock blockchain for testing."""
    blockchain = MockBlockchainState()
    blockchain.gas_price = Decimal("20000000000")  # 20 gwei in wei
    return blockchain


@pytest.fixture
def mock_contract(mock_blockchain):
    """Create mock staking contract for testing."""
    return MockStakingContract(mock_blockchain)


@pytest.fixture
def strategy():
    """Create auto-compound strategy for testing."""
    return ThresholdStrategy(
        min_reward_threshold=Decimal("0.5"),  # 0.5 token minimum
        max_gas_price=Decimal("100.0")  # 100 gwei max gas price
    )


@pytest.fixture
def monitor(test_address, strategy, mock_blockchain, mock_contract):
    """Create reward monitor for testing."""
    return RewardMonitor(
        address=test_address,
        strategy=strategy,
        blockchain=mock_blockchain,
        contract=mock_contract,
    )


def setup_test_account(
    mock_blockchain,
    mock_contract,
    address,
    balance=Decimal("10"),
    stake_amount=Decimal("5"),
    rewards=Decimal("0.05"),
):
    """Set up test account with specified balance and rewards."""
    # Create account first
    mock_blockchain.create_account(address, float(balance))
    # Set up staking state
    mock_contract.stakes[address] = stake_amount
    mock_contract.rewards[address] = rewards
    mock_contract.stake_block[address] = mock_blockchain.current_block


def test_check_rewards_below_minimum(
    monitor,
    mock_blockchain,
    mock_contract,
    test_address,
):
    """Test checking rewards below minimum threshold."""
    setup_test_account(
        mock_blockchain,
        mock_contract,
        test_address,
        balance=Decimal("10"),
        stake_amount=Decimal("5"),
        rewards=Decimal("0.05"),
    )
    
    decision = monitor.check_rewards()
    assert not decision
    assert monitor.contract.get_rewards(test_address) == Decimal("0.05")


def test_check_rewards_should_compound(
    monitor,
    mock_blockchain,
    mock_contract,
    test_address,
):
    """Test checking rewards above minimum threshold."""
    setup_test_account(
        mock_blockchain,
        mock_contract,
        test_address,
        balance=Decimal("10"),
        stake_amount=Decimal("5"),
        rewards=Decimal("1.0"),  # Above minimum
    )
    
    # Set favorable gas price
    mock_blockchain.gas_price = Decimal("15")  # Below average
    monitor.gas_optimizer.check_gas_price()  # Record initial price
    
    decision = monitor.check_rewards()
    assert decision


def test_check_rewards_high_gas(
    monitor,
    mock_blockchain,
    mock_contract,
    test_address,
):
    """Test checking rewards with high gas price."""
    setup_test_account(
        mock_blockchain,
        mock_contract,
        test_address,
        balance=Decimal("10"),
        stake_amount=Decimal("5"),
        rewards=Decimal("1.0"),  # Above minimum
    )
    
    # Set up increasing gas prices
    base_time = mock_blockchain.last_block_time
    for i in range(6):
        mock_blockchain.last_block_time = base_time + timedelta(minutes=i*5)
        mock_blockchain.gas_price = Decimal("20")
        monitor.gas_optimizer.check_gas_price()
    
    # Set very high gas price
    mock_blockchain.gas_price = Decimal("50")
    
    decision = monitor.check_rewards()
    assert not decision


def test_execute_compound_success(
    monitor,
    mock_blockchain,
    mock_contract,
    test_address,
):
    """Test successful compound execution."""
    setup_test_account(
        mock_blockchain,
        mock_contract,
        test_address,
        balance=Decimal("10"),
        stake_amount=Decimal("5"),
        rewards=Decimal("1.0"),  # Above minimum
    )
    
    # Set favorable gas price
    mock_blockchain.gas_price = Decimal("15")  # Below average
    monitor.gas_optimizer.check_gas_price()  # Record initial price
    
    event = monitor.execute_compound()
    assert event is not None
    assert event["status"] == "success"
    assert "value" in event
    assert event["value"] == "1.000000 ETH"


def test_execute_compound_insufficient_rewards(
    monitor,
    mock_blockchain,
    mock_contract,
    test_address,
):
    """Test compound execution with insufficient rewards."""
    setup_test_account(
        mock_blockchain,
        mock_contract,
        test_address,
        balance=Decimal("10"),
        stake_amount=Decimal("5"),
        rewards=Decimal("0.1"),  # Below minimum
    )
    
    event = monitor.execute_compound()
    assert event is None


def test_execute_compound_high_gas(
    monitor,
    mock_blockchain,
    mock_contract,
    test_address,
):
    """Test compound execution with high gas price."""
    setup_test_account(
        mock_blockchain,
        mock_contract,
        test_address,
        balance=Decimal("10"),
        stake_amount=Decimal("5"),
        rewards=Decimal("1.0"),  # Above minimum
    )
    
    # Set up increasing gas prices
    base_time = mock_blockchain.last_block_time
    for i in range(6):
        mock_blockchain.last_block_time = base_time + timedelta(minutes=i*5)
        mock_blockchain.gas_price = Decimal("20")
        monitor.gas_optimizer.check_gas_price()
    
    # Set very high gas price
    mock_blockchain.gas_price = Decimal("50")
    monitor.strategy.max_gas_price = Decimal("30")  # Lower than current gas price
    
    event = monitor.execute_compound()
    assert event is None


def test_compound_stats_empty(monitor):
    """Test compound statistics with no history."""
    stats = monitor.get_compound_stats()
    assert stats["total_compounds"] == 0
    assert stats["total_rewards_compounded"] == Decimal("0")
    assert stats["total_gas_cost"] == Decimal("0")
    assert stats["average_gas_cost"] == Decimal("0")


def test_compound_stats_with_history(
    monitor,
    mock_blockchain,
    mock_contract,
    test_address,
):
    """Test compound statistics with history."""
    setup_test_account(
        mock_blockchain,
        mock_contract,
        test_address,
        balance=Decimal("10"),
        stake_amount=Decimal("5"),
        rewards=Decimal("1.0"),
    )
    
    # Set favorable gas price
    mock_blockchain.gas_price = Decimal("15")
    monitor.gas_optimizer.check_gas_price()
    
    # Execute compound
    event = monitor.execute_compound()
    assert event is not None
    
    stats = monitor.get_compound_stats()
    assert stats["total_compounds"] == 1
    assert stats["total_rewards_compounded"] == Decimal("1.0")
    assert stats["total_gas_cost"] == Decimal("1500000")  # 15 wei * 100000 gas
    assert stats["average_gas_cost"] == Decimal("1500000")  # Same as total for one compound
