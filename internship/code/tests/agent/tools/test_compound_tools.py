"""Tests for auto-compound tools."""
import pytest
from decimal import Decimal
from unittest.mock import MagicMock

from src.staking_optimizer.blockchain import MockBlockchainState, MockStakingContract
from src.staking_optimizer.agent.tools.compound_tools import (
    create_compound_tools,
    CompoundArgs,
)


@pytest.fixture
def mock_blockchain():
    """Create a mock blockchain state."""
    mock = MockBlockchainState()
    mock.gas_price = Decimal("1000000000")
    mock.block_number = 1000000
    return mock


@pytest.fixture
def mock_contract(mock_blockchain):
    """Create a mock staking contract."""
    mock = MockStakingContract(blockchain=mock_blockchain)
    mock.blockchain.create_account("test_address", 10.0)  # Create account with 10 ETH
    mock.stakes["test_address"] = Decimal("5.0")
    mock.rewards["test_address"] = Decimal("1.0")
    mock.stake_block["test_address"] = 0  # Set initial stake block
    return mock


def test_create_compound_tools(mock_blockchain, mock_contract):
    """Test creation of compound tools."""
    tools = create_compound_tools(mock_blockchain, mock_contract)
    assert len(tools) == 3
    tool_names = {tool.name for tool in tools}
    assert tool_names == {
        "check_compound_status",
        "execute_compound",
        "get_compound_stats",
    }


def test_check_compound_status(mock_blockchain, mock_contract):
    """Test check compound status tool."""
    tools = create_compound_tools(mock_blockchain, mock_contract)
    check_tool = next(t for t in tools if t.name == "check_compound_status")
    
    # Call tool
    result = check_tool.func("test_address")
    assert isinstance(result, dict)
    assert result["can_compound"] == "true"
    assert result["rewards"] == "1.000000 ETH"


def test_execute_compound(mock_blockchain, mock_contract):
    """Test execute compound tool."""
    tools = create_compound_tools(mock_blockchain, mock_contract)
    compound_tool = next(t for t in tools if t.name == "execute_compound")
    
    # Call tool with all parameters
    args = CompoundArgs(
        address="test_address",
        min_rewards=Decimal("0.1"),
        max_gas_price=100000000000,
    )
    result = compound_tool.func(args)
    assert isinstance(result, dict)
    assert result["status"] == "success"
    assert result["value"] == "1.000000 ETH"


def test_execute_compound_minimal(mock_blockchain, mock_contract):
    """Test execute compound tool with minimal parameters."""
    tools = create_compound_tools(mock_blockchain, mock_contract)
    compound_tool = next(t for t in tools if t.name == "execute_compound")
    
    # Call tool with minimal parameters
    args = CompoundArgs(
        address="test_address",
        max_gas_price=2000000000,  # Higher than mock_blockchain.gas_price
    )
    result = compound_tool.func(args)
    assert isinstance(result, dict)
    assert result["status"] == "success"
    assert result["value"] == "1.000000 ETH"


def test_get_compound_stats(mock_blockchain, mock_contract):
    """Test get compound stats tool."""
    tools = create_compound_tools(mock_blockchain, mock_contract)
    stats_tool = next(t for t in tools if t.name == "get_compound_stats")
    
    # Call tool
    result = stats_tool.func("test_address")
    assert isinstance(result, dict)
    assert "last_compound" in result
    assert "total_compounds" in result
    assert "total_rewards_compounded" in result
    assert "total_gas_cost" in result
    assert "average_gas_cost" in result
