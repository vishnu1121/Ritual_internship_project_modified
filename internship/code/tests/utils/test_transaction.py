"""Tests for transaction formatting utilities."""

from decimal import Decimal

import pytest

from staking_optimizer.blockchain import MockTransaction
from staking_optimizer.utils import format_transaction


def test_format_mock_transaction():
    """Test formatting a MockTransaction."""
    tx = MockTransaction(
        from_address="0xabc",
        to_address="0xdef",
        value=Decimal("1.234567"),
        nonce=0,
        gas_price=Decimal("50000000000"),  # 50 gwei in wei
        gas_limit=21000,
        gas_used=19950,  # Actual gas used
        status="success"
    )
    
    result = format_transaction(tx)
    expected = {
        "from": "0xabc",
        "to": "0xdef",
        "value": "1.234567 ETH",
        "gas_used": "19950",  # Actual gas used
        "gas_price": "50.00 gwei",
        "status": "success"
    }
    
    # Check hash format but not exact value
    assert result["hash"].startswith("0x")
    assert len(result["hash"]) == 66  # 0x + 64 hex chars
    
    # Check all other fields
    for key, value in expected.items():
        assert result[key] == value


def test_format_dict_transaction():
    """Test formatting a transaction dictionary."""
    tx = {
        "hash": "0x123",
        "from": "0xabc",
        "to": "0xdef",
        "value": "1.234567 ETH",
        "gas_used": 21000,
        "gas_price": "50.00 gwei",
        "status": "confirmed"
    }
    
    result = format_transaction(tx)
    assert result == {
        "hash": "0x123",
        "from": "0xabc",
        "to": "0xdef",
        "value": "1.234567 ETH",
        "gas_used": "21000",
        "gas_price": "50.00 gwei",
        "status": "success"  # confirmed mapped to success
    }


def test_format_dict_numeric_values():
    """Test formatting a dictionary with numeric values."""
    tx = {
        "hash": "0x123",
        "from": "0xabc",
        "to": "0xdef",
        "value": 1.234567,
        "gas_used": 21000,
        "gas_price": 50,
        "status": "pending"
    }
    
    result = format_transaction(tx)
    assert result == {
        "hash": "0x123",
        "from": "0xabc",
        "to": "0xdef",
        "value": "1.234567 ETH",
        "gas_used": "21000",
        "gas_price": "50.00 gwei",
        "status": "pending"
    }


@pytest.mark.parametrize("status,expected", [
    ("pending", "pending"),
    ("success", "success"),
    ("confirmed", "success"),
    ("failed", "failed"),
    ("reverted", "failed"),
    ("unknown", "unknown"),
])
def test_status_mapping(status, expected):
    """Test different transaction status mappings."""
    tx = MockTransaction(
        from_address="0xabc",
        to_address="0xdef",
        value=Decimal("0"),
        nonce=0,
        gas_price=Decimal("50000000000"),
        status=status
    )
    
    result = format_transaction(tx)
    assert result["status"] == expected


def test_missing_optional_fields():
    """Test handling of missing optional fields in dict input."""
    tx = {
        "hash": "0x123",
        "from": "0xabc",
        "status": "pending"
    }
    
    result = format_transaction(tx)
    assert result == {
        "hash": "0x123",
        "from": "0xabc",
        "to": "",
        "value": "0.000000 ETH",
        "gas_used": "0",
        "gas_price": "0.00 gwei",
        "status": "pending"
    }
