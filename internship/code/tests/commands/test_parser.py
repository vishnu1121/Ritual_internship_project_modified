"""Tests for the command parser module."""

import pytest
from decimal import Decimal
from src.staking_optimizer.commands.parser import CommandParser, CommandParseError
from src.staking_optimizer.commands.models import (
    StakeCommand, UnstakeCommand, CompoundCommand, ViewCommand, InformationalCommand
)


@pytest.fixture
def parser():
    """Create a command parser instance."""
    return CommandParser(model_name="openai/gpt-4o-2024-11-20", temperature=0.0)


def test_parse_stake_command(parser):
    """Test parsing stake command."""
    text = "stake 100 ETH from 0x1234567890123456789012345678901234567890"
    command = parser.parse_request(text)
    assert isinstance(command, StakeCommand)
    assert command.address == "0x1234567890123456789012345678901234567890"
    assert command.amount == 100.0


def test_parse_unstake_command(parser):
    """Test parsing unstake command."""
    text = "unstake 50 ETH from 0x1234567890123456789012345678901234567890"
    command = parser.parse_request(text)
    assert isinstance(command, UnstakeCommand)
    assert command.address == "0x1234567890123456789012345678901234567890"
    assert command.amount == Decimal('50.0')
    assert not command.unstake_all


def test_parse_unstake_all_command(parser):
    """Test parsing unstake all command."""
    text = "unstake all ETH from 0x1234567890123456789012345678901234567890"
    command = parser.parse_request(text)
    assert isinstance(command, UnstakeCommand)
    assert command.address == "0x1234567890123456789012345678901234567890"
    assert command.unstake_all


def test_parse_compound_command(parser):
    """Test parsing compound command."""
    text = "compound rewards for 0x1234567890123456789012345678901234567890"
    command = parser.parse_request(text)
    assert isinstance(command, CompoundCommand)
    assert command.address == "0x1234567890123456789012345678901234567890"


def test_parse_view_command(parser):
    """Test parsing view command."""
    text = "view staking position for 0x1234567890123456789012345678901234567890"
    command = parser.parse_request(text)
    assert isinstance(command, ViewCommand)
    assert command.address == "0x1234567890123456789012345678901234567890"
    assert command.view_type == "position"


def test_parse_info_command(parser):
    """Test parsing informational command."""
    text = "what is the APR strategy?"
    command = parser.parse_request(text)
    assert isinstance(command, InformationalCommand)
    assert command.topic == "apr_strategy"


def test_parse_invalid_command(parser):
    """Test parsing invalid command."""
    text = "invalid command without address"
    with pytest.raises(CommandParseError):
        parser.parse_request(text)
