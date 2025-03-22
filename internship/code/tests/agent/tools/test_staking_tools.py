"""Tests for staking tools."""
import pytest
from decimal import Decimal
from unittest.mock import MagicMock

from src.staking_optimizer.blockchain import MockBlockchainState, MockStakingContract
from src.staking_optimizer.agent.tools.staking_tools import (
    create_staking_tools,
    StakeArgs,
    UnstakeArgs,
    ClaimArgs,
    ViewArgs,
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
    mock.stake_block["test_address"] = 0  # Set initial stake block
    return mock


def test_create_staking_tools(mock_blockchain, mock_contract):
    """Test creation of staking tools."""
    tools = create_staking_tools(mock_blockchain, mock_contract)
    assert len(tools) == 8
    tool_names = {tool.name for tool in tools}
    assert tool_names == {
        "view_staking_position",
        "GetStakingAPR",
        "GetGasPrice",
        "GetAccountBalance",
        "Stake",
        "stake_tokens",
        "unstake_tokens",
        "claim_rewards",
    }


def test_view_staking_position(mock_blockchain, mock_contract):
    """Test view staking position tool."""
    tools = create_staking_tools(mock_blockchain, mock_contract)
    view_tool = next(t for t in tools if t.name == "view_staking_position")

    # Call tool
    args = ViewArgs(address="test_address")
    result = view_tool.func(args)
    assert isinstance(result, dict)
    assert result["address"] == "test_address"
    assert result["staked"] == "0.000000 ETH"
    assert result["rewards"] == "0.000000 ETH"
    assert result["apr"] == "5.0%"


def test_stake_tokens(mock_blockchain, mock_contract):
    """Test stake tokens tool."""
    tools = create_staking_tools(mock_blockchain, mock_contract)
    stake_tool = next(t for t in tools if t.name == "Stake")

    # Call tool
    args = StakeArgs(address="test_address", amount=Decimal("1.0"))
    result = stake_tool.func(args)
    assert isinstance(result, dict)
    assert result["status"] == "success"
    assert result["value"] == "1.000000 ETH"


def test_unstake_tokens(mock_blockchain, mock_contract):
    """Test unstake tokens tool."""
    tools = create_staking_tools(mock_blockchain, mock_contract)
    
    # First stake some tokens
    stake_tool = next(t for t in tools if t.name == "Stake")
    stake_args = StakeArgs(address="test_address", amount=Decimal("2.0"))
    stake_result = stake_tool.func(stake_args)
    assert stake_result["status"] == "success"
    assert mock_contract.stakes["test_address"] == Decimal("2.0")
    
    # Then try to unstake half
    unstake_tool = next(t for t in tools if t.name == "unstake_tokens")
    unstake_args = UnstakeArgs(address="test_address", amount=Decimal("1.0"))
    result = unstake_tool.func(unstake_args)
    
    assert isinstance(result, dict)
    assert result["status"] == "success"
    assert result["value"] == "0.000000 ETH"  # Transaction value is 0 since contract handles balance internally
    assert mock_contract.stakes["test_address"] == Decimal("1.0")  # Verify remaining stake


def test_claim_rewards(mock_blockchain, mock_contract):
    """Test claim rewards tool."""
    tools = create_staking_tools(mock_blockchain, mock_contract)
    
    # First stake some tokens and add rewards
    stake_tool = next(t for t in tools if t.name == "Stake")
    stake_args = StakeArgs(address="test_address", amount=Decimal("2.0"))
    stake_result = stake_tool.func(stake_args)
    assert stake_result["status"] == "success"
    
    # Add some rewards
    mock_contract.add_rewards("test_address", Decimal("1.0"))
    assert mock_contract.rewards["test_address"] == Decimal("1.0")
    
    # Then claim rewards
    claim_tool = next(t for t in tools if t.name == "claim_rewards")
    claim_args = ClaimArgs(address="test_address")
    result = claim_tool.func(claim_args)
    
    assert isinstance(result, dict)
    assert result["status"] == "success"
    assert result["value"] == "1.000000 ETH"  # Transaction value should be the claimed rewards
    assert mock_contract.rewards["test_address"] == Decimal("0")  # Rewards should be reset to 0
