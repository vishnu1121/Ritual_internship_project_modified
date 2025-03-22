"""Tests for gas optimization functionality."""

from datetime import datetime, timedelta
from decimal import Decimal

import pytest
from src.staking_optimizer.autocompound.optimizer import GasOptimizer
from src.staking_optimizer.blockchain.mock_state import MockBlockchainState


@pytest.fixture
def mock_blockchain():
    """Create mock blockchain for testing."""
    blockchain = MockBlockchainState()
    blockchain.gas_price = Decimal("20")  # Set reasonable gas price
    return blockchain


@pytest.fixture
def optimizer(mock_blockchain):
    """Create gas optimizer for testing."""
    return GasOptimizer(
        blockchain=mock_blockchain,
        window_size=60,  # 60 minute window
        min_window_size=5,  # 5 minute minimum window
    )


def test_initial_gas_stats(optimizer):
    """Test gas statistics with no history."""
    stats = optimizer.get_gas_stats()
    assert stats["average_gas_price"] == Decimal("0")
    assert stats["min_gas_price"] == Decimal("0")
    assert stats["max_gas_price"] == Decimal("0")
    assert stats["current_gas_price"] == Decimal("20")


def test_check_gas_price_single(optimizer, mock_blockchain):
    """Test checking gas price with single data point."""
    # Single price should create a window
    result = optimizer.check_gas_price()
    assert result  # Single price is always "optimal"
    
    stats = optimizer.get_gas_stats()
    assert stats["average_gas_price"] == Decimal("20")
    assert stats["min_gas_price"] == Decimal("20")
    assert stats["max_gas_price"] == Decimal("20")


def test_check_gas_price_window(optimizer, mock_blockchain):
    """Test checking gas price with multiple data points."""
    # Create price history over 30 minutes with fluctuating prices
    base_time = mock_blockchain.last_block_time
    prices = [20, 22, 18, 21, 19, 23]  # Fluctuating prices
    
    for i, price in enumerate(prices):
        mock_blockchain.last_block_time = base_time + timedelta(minutes=i*5)
        mock_blockchain.gas_price = Decimal(str(price))
        optimizer.check_gas_price()
    
    # Reset time to when price was low (18)
    mock_blockchain.last_block_time = base_time + timedelta(minutes=10)
    mock_blockchain.gas_price = Decimal("19")  # Below average price
    
    # Should be favorable since price is below average
    assert optimizer.check_gas_price()
    
    # Try with high price
    mock_blockchain.gas_price = Decimal("25")
    assert not optimizer.check_gas_price()


def test_check_gas_price_no_window(optimizer, mock_blockchain):
    """Test checking gas price with no favorable window."""
    # Create price history over 30 minutes with high prices
    base_time = mock_blockchain.last_block_time
    for i in range(6):
        mock_blockchain.last_block_time = base_time + timedelta(minutes=i*5)
        mock_blockchain.gas_price = Decimal("100")  # High gas price
        optimizer.check_gas_price()
    
    # Set current price higher than average
    mock_blockchain.last_block_time = base_time + timedelta(minutes=15)
    mock_blockchain.gas_price = Decimal("150")
    
    # Should not be favorable
    assert not optimizer.check_gas_price()


def test_window_cleanup(optimizer, mock_blockchain):
    """Test that old prices are removed from window."""
    # Create old prices outside window
    base_time = mock_blockchain.last_block_time
    for i in range(12):  # 1 hour of data
        mock_blockchain.last_block_time = base_time + timedelta(minutes=i*5)
        mock_blockchain.gas_price = Decimal("20")
        optimizer.check_gas_price()
    
    # Move to future
    mock_blockchain.last_block_time = base_time + timedelta(hours=2)
    optimizer.check_gas_price()
    
    # Should only have one price in history
    assert len(optimizer.price_history) == 1
