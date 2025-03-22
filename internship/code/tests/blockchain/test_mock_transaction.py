"""Tests for mock blockchain transaction functionality.

This module contains unit tests for the MockTransaction class, verifying core
transaction functionality including:
    - Transaction initialization and validation
    - State transitions (confirmation/failure)
    - Gas cost calculations
    - Dictionary serialization

The tests ensure that transactions behave correctly in both success and failure
scenarios, properly track gas costs, and maintain consistent state.
"""

from decimal import Decimal

import pytest

from src.staking_optimizer.blockchain.mock_transaction import MockTransaction


@pytest.fixture
def transaction():
    """Create a basic mock transaction for testing.

    Creates a transaction with standard test values:
        - from_address: "0x123"
        - to_address: "0x456"
        - value: 1.0 ETH
        - nonce: 0
        - gas_price: 20 gwei

    Returns:
        MockTransaction: A new transaction instance with test values
    """
    return MockTransaction(
        from_address="0x123",
        to_address="0x456",
        value=Decimal("1.0"),
        nonce=0,
        gas_price=Decimal("20000000000")
    )


def test_transaction_initialization(transaction):
    """Test that transaction is initialized with correct values.

    Verifies that:
        1. Addresses are set correctly
        2. Value and nonce match inputs
        3. Gas price is set as specified
        4. Status starts as 'pending'
        5. Hash is properly formatted (0x + 64 hex chars)
        6. Timestamp is set

    Args:
        transaction: Fixture providing a basic mock transaction
    """
    assert transaction.from_address == "0x123"
    assert transaction.to_address == "0x456"
    assert transaction.value == Decimal("1.0")
    assert transaction.nonce == 0
    assert transaction.gas_price == Decimal("20000000000")
    assert transaction.status == "pending"
    assert transaction.hash.startswith("0x")
    assert len(transaction.hash) == 66  # 0x + 64 hex chars
    assert transaction.timestamp is not None


def test_transaction_confirmation(transaction):
    """Test successful transaction confirmation.

    Verifies that:
        1. Status changes to 'success'
        2. Error remains None
        3. Gas used is set appropriately

    Args:
        transaction: Fixture providing a basic mock transaction
    """
    transaction.confirm()
    assert transaction.status == "success"
    assert transaction.error is None


def test_transaction_failure(transaction):
    """Test transaction failure handling.

    Verifies that:
        1. Status changes to 'failed'
        2. Error message is set correctly
        3. Gas used reflects failed transaction

    Args:
        transaction: Fixture providing a basic mock transaction
    """
    error_message = "Insufficient gas"
    transaction.confirm(success=False, error=error_message)
    assert transaction.status == "failed"
    assert transaction.error == error_message


def test_gas_cost_calculation(transaction):
    """Test accurate gas cost calculation.

    Verifies that:
        1. Gas cost is calculated as gas_used * gas_price
        2. Gas used is set to gas_limit for successful transactions
        3. Gas cost matches expected value

    Args:
        transaction: Fixture providing a basic mock transaction
    """
    # Gas cost should be in ETH (gas_price * gas_limit / 10^18)
    expected_cost = transaction.gas_price * transaction.gas_limit / Decimal("1000000000000000000")
    assert transaction.get_gas_cost() == expected_cost


def test_transaction_to_dict(transaction):
    """Test transaction dictionary conversion.

    Verifies that:
        1. Dictionary contains all expected keys
        2. Values match transaction attributes

    Args:
        transaction: Fixture providing a basic mock transaction
    """
    tx_dict = transaction.to_dict()
    assert tx_dict["from"] == transaction.from_address
    assert tx_dict["to"] == transaction.to_address
    assert tx_dict["value"] == str(transaction.value)
    assert tx_dict["nonce"] == transaction.nonce
    assert tx_dict["gas_price"] == str(transaction.gas_price)
    assert tx_dict["gas_limit"] == transaction.gas_limit
    assert tx_dict["status"] == transaction.status
    assert tx_dict["hash"] == transaction.hash
    assert tx_dict["timestamp"] is not None
