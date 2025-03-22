"""Tests for the response templates module."""

import pytest
from src.staking_optimizer.commands.templates import ResponseTemplates, ResponseType, TemplateError


@pytest.fixture
def templates():
    """Create a response templates instance."""
    return ResponseTemplates()


def test_response_type_enum():
    """Test ResponseType enum values."""
    assert ResponseType.SUCCESS == "success"
    assert ResponseType.ERROR == "error"
    assert ResponseType.INFO == "info"
    assert ResponseType.HELP == "help"


def test_template_initialization(templates):
    """Test template initialization."""
    assert templates.templates is not None
    assert "stake_success" in templates.templates
    assert "unstake_success" in templates.templates
    assert "compound_success" in templates.templates
    assert "claim_success" in templates.templates


def test_get_template(templates):
    """Test getting templates."""
    # Test existing template
    template = templates.get_template("stake_success")
    assert template is not None
    
    # Test non-existent template
    template = templates.get_template("non_existent")
    assert template is None


def test_format_stake_success(templates):
    """Test formatting stake success message."""
    response = templates.format_response(
        "stake_success",
        amount=100,
        token="ETH",
        validator="0x123",
        tx_hash="0xabc",
        position="100 ETH staked"
    )
    assert "Successfully staked 100 ETH" in response
    assert "0x123" in response
    assert "0xabc" in response
    assert "100 ETH staked" in response


def test_format_unstake_success(templates):
    """Test formatting unstake success message."""
    response = templates.format_response(
        "unstake_success",
        amount=50,
        token="ETH",
        tx_hash="0xabc",
        balance="50 ETH"
    )
    assert "Successfully unstaked 50 ETH" in response
    assert "0xabc" in response
    assert "50 ETH" in response


def test_format_compound_success(templates):
    """Test formatting compound success message."""
    response = templates.format_response(
        "compound_success",
        amount=10,
        token="ETH",
        tx_hash="0xabc",
        position="110 ETH staked"
    )
    assert "Successfully compounded 10 ETH" in response
    assert "0xabc" in response
    assert "110 ETH staked" in response


def test_format_claim_success(templates):
    """Test formatting claim success message."""
    response = templates.format_response(
        "claim_success",
        amount=5,
        token="ETH",
        tx_hash="0xabc",
        address="0x123"
    )
    assert "Successfully claimed 5 ETH" in response
    assert "0xabc" in response
    assert "0x123" in response


def test_format_insufficient_balance_error(templates):
    """Test formatting insufficient balance error."""
    response = templates.format_response(
        "insufficient_balance",
        action="stake",
        required=100,
        token="ETH",
        available=50
    )
    assert "Insufficient balance" in response
    assert "100 ETH" in response
    assert "50 ETH" in response


def test_format_invalid_amount_error(templates):
    """Test formatting invalid amount error."""
    response = templates.format_response(
        "invalid_amount",
        min_amount=1,
        max_amount=1000,
        token="ETH"
    )
    assert "Invalid amount" in response
    assert "1" in response
    assert "1000" in response
    assert "ETH" in response


def test_format_position_info(templates):
    """Test formatting position info message."""
    response = templates.format_response(
        "position_info",
        staked=100,
        token="ETH",
        validator="0x123",
        rewards=5,
        apr=10
    )
    assert "Current Staking Position" in response
    assert "100 ETH" in response
    assert "0x123" in response
    assert "5 ETH" in response
    assert "10%" in response


def test_format_missing_template(templates):
    """Test formatting with missing template."""
    with pytest.raises(ValueError):
        templates.format_response("non_existent")


def test_format_missing_variables(templates):
    """Test formatting with missing variables."""
    with pytest.raises(TemplateError):
        templates.format_response("stake_success", amount=100)  # Missing other required variables
