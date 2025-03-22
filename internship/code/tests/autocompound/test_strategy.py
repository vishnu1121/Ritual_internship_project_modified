"""Test auto-compound strategies."""

from datetime import datetime, timedelta
from decimal import Decimal

import pytest

from src.staking_optimizer.autocompound.strategy import (
    CompoundDecision,
    ThresholdStrategy,
    TimeBasedStrategy,
)
from src.staking_optimizer.types import StakingPosition
from src.staking_optimizer.blockchain.mock_state import MockBlockchainState


@pytest.fixture
def mock_blockchain():
    """Create mock blockchain."""
    state = MockBlockchainState()
    state.gas_price = Decimal("20")  # Set reasonable gas price for testing
    return state


@pytest.fixture
def mock_position():
    """Create mock staking position."""
    return StakingPosition(
        address="0x123",
        staked=Decimal("100"),
        rewards=Decimal("1.0"),
        apr=Decimal("0.1"),
    )


def test_threshold_strategy_below_threshold(mock_blockchain, mock_position):
    """Test threshold strategy when rewards are below threshold."""
    strategy = ThresholdStrategy(
        min_reward_threshold=Decimal("2.0"),
        max_gas_price=Decimal("100"),
    )
    
    decision = strategy.should_compound(mock_position, mock_blockchain)
    assert not decision.should_compound
    assert "below threshold" in decision.reason
    assert decision.min_reward_threshold == Decimal("2.0")


def test_threshold_strategy_high_gas(mock_blockchain, mock_position):
    """Test threshold strategy when gas price is too high."""
    strategy = ThresholdStrategy(
        min_reward_threshold=Decimal("0.5"),
        max_gas_price=Decimal("50"),
    )
    
    mock_blockchain.set_gas_price(Decimal("100"))  # Set high gas price
    
    decision = strategy.should_compound(mock_position, mock_blockchain)
    assert not decision.should_compound
    assert "exceeds threshold" in decision.reason
    assert decision.gas_price_threshold == Decimal("50")


def test_threshold_strategy_should_compound(mock_blockchain, mock_position):
    """Test threshold strategy when conditions are favorable."""
    strategy = ThresholdStrategy(
        min_reward_threshold=Decimal("0.5"),
        max_gas_price=Decimal("100"),
    )
    
    mock_blockchain.gas_price = Decimal("20")  # Set reasonable gas price
    
    decision = strategy.should_compound(mock_position, mock_blockchain)
    assert decision.should_compound
    assert "exceed threshold" in decision.reason
    assert decision.min_reward_threshold == Decimal("0.5")
    assert decision.gas_price_threshold == Decimal("100")


def test_time_based_strategy_first_compound(mock_blockchain, mock_position):
    """Test time-based strategy on first compound."""
    strategy = TimeBasedStrategy(
        compound_interval=timedelta(days=1),
        min_reward_threshold=Decimal("0.5"),
        max_gas_price=Decimal("100"),
    )
    
    decision = strategy.should_compound(mock_position, mock_blockchain)
    assert decision.should_compound
    assert "reached with favorable conditions" in decision.reason


def test_time_based_strategy_wait_interval(mock_blockchain, mock_position):
    """Test time-based strategy when waiting for interval."""
    strategy = TimeBasedStrategy(
        compound_interval=timedelta(days=1),
        min_reward_threshold=Decimal("0.5"),
        max_gas_price=Decimal("100"),
    )
    
    # First compound
    strategy.should_compound(mock_position, mock_blockchain)
    
    # Try again too soon
    mock_blockchain.last_block_time += timedelta(hours=12)
    
    decision = strategy.should_compound(mock_position, mock_blockchain)
    assert not decision.should_compound
    assert "Waiting" in decision.reason


def test_time_based_strategy_interval_reached(mock_blockchain, mock_position):
    """Test time-based strategy when interval is reached."""
    strategy = TimeBasedStrategy(
        compound_interval=timedelta(days=1),
        min_reward_threshold=Decimal("0.5"),
        max_gas_price=Decimal("100"),
    )
    
    # First compound
    strategy.should_compound(mock_position, mock_blockchain)
    
    # Wait for interval
    mock_blockchain.last_block_time += timedelta(days=2)
    mock_blockchain.gas_price = Decimal("20")  # Set reasonable gas price
    
    decision = strategy.should_compound(mock_position, mock_blockchain)
    assert decision.should_compound
    assert "reached with favorable conditions" in decision.reason
