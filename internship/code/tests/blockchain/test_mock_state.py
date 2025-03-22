"""Tests for mock blockchain state.

This module contains tests for the MockBlockchainState class, which provides a mock
implementation of blockchain state for testing staking operations. Tests cover account
management, ETH transfers, gas price management, block mining, and staking rewards.

Typical usage example:
    blockchain = MockBlockchainState(chain_id=1)
    account = blockchain.create_account("0x123", 1.0)
    tx = blockchain.transfer("0x123", "0x456", 0.5)
"""

from decimal import Decimal

import pytest

from src.staking_optimizer.blockchain.mock_state import MockBlockchainState


@pytest.fixture
def blockchain():
    """Create mock blockchain instance for testing.
    
    Returns:
        MockBlockchainState: A fresh blockchain instance with chain_id=1.
    """
    return MockBlockchainState(chain_id=1)


def test_create_account(blockchain):
    """Test account creation with initial balance.
    
    Tests that:
    1. Account is created with correct address and balance
    2. Initial nonce and staked amount are 0
    
    Args:
        blockchain: Pytest fixture providing MockBlockchainState instance
    """
    address = "0x123"
    balance = Decimal("1.5")
    
    account = blockchain.create_account(address, balance)
    assert account.address == address
    assert account.balance == balance
    assert account.nonce == 0
    assert account.staked_amount == 0


def test_create_duplicate_account(blockchain):
    """Test that creating a duplicate account raises ValueError.
    
    Tests that attempting to create an account with an existing address
    raises a ValueError.
    
    Args:
        blockchain: Pytest fixture providing MockBlockchainState instance
    """
    address = "0x123"
    blockchain.create_account(address)
    
    with pytest.raises(ValueError):
        blockchain.create_account(address)


def test_get_nonexistent_account(blockchain):
    """Test that getting a nonexistent account raises KeyError.
    
    Tests that attempting to get an account that doesn't exist raises
    a KeyError.
    
    Args:
        blockchain: Pytest fixture providing MockBlockchainState instance
    """
    with pytest.raises(KeyError):
        blockchain.get_account("0x123")


def test_transfer(blockchain):
    """Test ETH transfer between accounts.
    
    Tests that:
    1. Transfer updates sender and recipient balances correctly
    2. Gas cost is deducted from sender
    3. Transaction is recorded with correct details
    
    Args:
        blockchain: Pytest fixture providing MockBlockchainState instance
    """
    from_addr = "0x123"
    to_addr = "0x456"
    initial_balance = Decimal("2.0")
    transfer_amount = Decimal("1.0")
    
    blockchain.create_account(from_addr, initial_balance)
    tx = blockchain.transfer(from_addr, to_addr, transfer_amount)
    
    # Calculate gas cost in ETH
    gas_cost = (tx.gas_used * tx.gas_price) / Decimal("1000000000000000000")  # Convert wei to ETH
    
    assert tx.from_address == from_addr
    assert tx.to_address == to_addr
    assert tx.value == transfer_amount
    assert blockchain.get_account(from_addr).balance == initial_balance - transfer_amount - gas_cost
    assert blockchain.get_account(to_addr).balance == transfer_amount


def test_transfer_insufficient_balance(blockchain):
    """Test that transfer with insufficient balance raises ValueError.
    
    Tests that attempting to transfer more ETH than the sender has
    raises a ValueError.
    
    Args:
        blockchain: Pytest fixture providing MockBlockchainState instance
    """
    from_addr = "0x123"
    to_addr = "0x456"
    blockchain.create_account(from_addr, Decimal("1.0"))
    
    with pytest.raises(ValueError):
        blockchain.transfer(from_addr, to_addr, Decimal("2.0"))


def test_mine_block(blockchain):
    """Test mining block updates state.
    
    Tests that mining a block increments the block number.
    
    Args:
        blockchain: Pytest fixture providing MockBlockchainState instance
    """
    initial_block = blockchain.get_block_number()
    blockchain.mine_block()
    assert blockchain.get_block_number() == initial_block + 1


def test_gas_price(blockchain):
    """Test gas price management.
    
    Tests that:
    1. Initial gas price is set correctly
    2. Gas price can be updated successfully
    
    Args:
        blockchain: Pytest fixture providing MockBlockchainState instance
    """
    initial_price = blockchain.get_gas_price()
    new_price = Decimal("25000000000")
    
    blockchain.set_gas_price(new_price)
    assert blockchain.get_gas_price() == new_price
    assert blockchain.get_gas_price() != initial_price


def test_staking_rewards(blockchain):
    """Test staking rewards calculation.
    
    Tests that staking rewards are calculated correctly after mining a block.
    
    Args:
        blockchain: Pytest fixture providing MockBlockchainState instance
    """
    address = "0x123"
    stake_amount = Decimal("10.0")
    blockchain.create_account(address, stake_amount)
    
    account = blockchain.get_account(address)
    account.staked_amount = stake_amount
    account.last_stake_time = blockchain.last_block_time
    
    # Mine a block to trigger reward calculation
    blockchain.mine_block()
    
    assert account.rewards > 0
