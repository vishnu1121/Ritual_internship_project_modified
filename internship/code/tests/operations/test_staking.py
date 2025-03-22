"""Tests for staking operations.

This module contains tests for the staking operations, including staking,
unstaking, and reward management.
"""
import logging
from decimal import Decimal
from typing import Dict

import pytest

from src.staking_optimizer.blockchain.mock_state import MockBlockchainState
from src.staking_optimizer.blockchain.mock_contract import MockStakingContract
from src.staking_optimizer.operations.stake import stake_tokens
from src.staking_optimizer.operations.unstake import unstake_tokens
from src.staking_optimizer.operations.view import get_staking_position_mock, format_position
from src.staking_optimizer.operations.claim import claim_rewards
from src.staking_optimizer.utils import format_transaction

logger = logging.getLogger(__name__)

@pytest.fixture
def blockchain() -> MockBlockchainState:
    """Create a fresh blockchain state for each test.

    Returns:
        A new instance of MockBlockchainState
    """
    return MockBlockchainState()


@pytest.fixture
def contract(blockchain: MockBlockchainState) -> MockStakingContract:
    """Create mock staking contract.

    Args:
        blockchain: The blockchain state to use

    Returns:
        A new instance of MockStakingContract
    """
    contract = MockStakingContract(blockchain)
    try:
        blockchain.create_account(contract.address, Decimal("1000.0"))  # Give contract some initial balance
    except ValueError:
        # Account already exists, just update the balance
        account = blockchain.get_account(contract.address)
        account.balance = Decimal("1000.0")
    return contract


@pytest.fixture
def account() -> Dict[str, str]:
    """Create a test account.

    Returns:
        A dictionary containing the test account's address
    """
    return {"address": "0x742d35Cc6634C0532925a3b844Bc454e4438f44e"}


def test_view_empty_position(blockchain: MockBlockchainState, contract: MockStakingContract, account: Dict[str, str]) -> None:
    """Test viewing position with no stake.

    Args:
        blockchain: Mock blockchain state
        contract: Mock staking contract
        account: Test account information
    """
    blockchain.create_account(account["address"], Decimal("10.0"))
    position = get_staking_position_mock(account["address"], blockchain, contract)
    formatted = format_position(position)
    
    # Check staking position
    assert formatted["staked"] == "0.000000 ETH"
    
    # Check balance directly from blockchain
    balance = blockchain.get_balance(account["address"])
    assert balance == Decimal("10.0")
    assert formatted["rewards"] == "0.000000 ETH"


def test_stake_tokens(blockchain: MockBlockchainState, contract: MockStakingContract, account: Dict[str, str]) -> None:
    """Test staking tokens.

    Args:
        blockchain: Mock blockchain state
        contract: Mock staking contract
        account: Test account information
    """
    # Give account sufficient balance for stake + gas
    blockchain.create_account(account["address"], Decimal("15.0"))
    
    # Stake 5 ETH
    result = stake_tokens(account["address"], Decimal("5.0"), blockchain, contract)
    
    assert result["status"] == "success"
    assert result["hash"] is not None
    
    # Check position after staking
    position = get_staking_position_mock(account["address"], blockchain, contract)
    formatted = format_position(position)
    
    assert formatted["staked"] == "5.000000 ETH"
    
    # Check balance directly from blockchain
    balance = blockchain.get_balance(account["address"])
    assert balance < Decimal("10.0")  # Account for gas


def test_stake_insufficient_balance(blockchain: MockBlockchainState, contract: MockStakingContract, account: Dict[str, str]) -> None:
    """Test staking with insufficient balance.

    Args:
        blockchain: Mock blockchain state
        contract: Mock staking contract
        account: Test account information
    """
    blockchain.create_account(account["address"], Decimal("1.0"))
    with pytest.raises(ValueError, match="Insufficient balance"):
        stake_tokens(account["address"], Decimal("2.0"), blockchain, contract)


def test_unstake_tokens(blockchain: MockBlockchainState, contract: MockStakingContract, account: Dict[str, str]) -> None:
    """Test unstaking tokens.

    Args:
        blockchain: Mock blockchain state
        contract: Mock staking contract
        account: Test account information
    """
    # Give account sufficient balance for stake + gas
    blockchain.create_account(account["address"], Decimal("15.0"))
    
    # First stake some tokens
    stake_tokens(account["address"], Decimal("5.0"), blockchain, contract)
    
    # Then unstake half
    result = unstake_tokens(account["address"], Decimal("2.5"), blockchain, contract)
    
    assert result["status"] == "success"
    assert result["hash"] is not None
    
    # Check position after unstaking
    position = get_staking_position_mock(account["address"], blockchain, contract)
    formatted = format_position(position)
    assert formatted["staked"] == "2.500000 ETH"


def test_unstake_too_much(blockchain: MockBlockchainState, contract: MockStakingContract, account: Dict[str, str]) -> None:
    """Test unstaking more than staked amount.

    Args:
        blockchain: Mock blockchain state
        contract: Mock staking contract
        account: Test account information
    """
    # Give account sufficient balance for stake + gas
    blockchain.create_account(account["address"], Decimal("15.0"))
    
    stake_tokens(account["address"], Decimal("3.0"), blockchain, contract)
    
    with pytest.raises(ValueError, match="Insufficient staked balance"):
        unstake_tokens(account["address"], Decimal("4.0"), blockchain, contract)


def test_unstake_all(blockchain: MockBlockchainState, contract: MockStakingContract, account: Dict[str, str]) -> None:
    """Test unstaking all tokens.

    Args:
        blockchain: Mock blockchain state
        contract: Mock staking contract
        account: Test account information
    """
    # Give account sufficient balance for stake + gas
    blockchain.create_account(account["address"], Decimal("15.0"))
    
    # First stake some tokens
    stake_tokens(account["address"], Decimal("5.0"), blockchain, contract)
    
    # Then unstake all
    result = unstake_tokens(account["address"], Decimal("5.0"), blockchain, contract)
    
    assert result["status"] == "success"
    assert result["hash"] is not None
    
    # Check position after unstaking
    position = get_staking_position_mock(account["address"], blockchain, contract)
    formatted = format_position(position)
    assert formatted["staked"] == "0.000000 ETH"


def test_rewards_calculation(blockchain: MockBlockchainState, contract: MockStakingContract, account: Dict[str, str]) -> None:
    """Test reward calculations.

    Args:
        blockchain: Mock blockchain state
        contract: Mock staking contract
        account: Test account information
    """
    # Give account sufficient balance for stake + gas
    blockchain.create_account(account["address"], Decimal("15.0"))
    
    # Stake tokens and mine some blocks to generate rewards
    stake_tokens(account["address"], Decimal("10.0"), blockchain, contract)
    
    # Mine some blocks to generate rewards
    for _ in range(10):
        blockchain.mine_block()
    
    # Check rewards
    position = get_staking_position_mock(account["address"], blockchain, contract)
    formatted = format_position(position)
    rewards = Decimal(formatted["rewards"].rstrip(" ETH"))
    assert rewards > 0


def test_claim_rewards(blockchain: MockBlockchainState, contract: MockStakingContract, account: Dict[str, str]) -> None:
    """Test claiming rewards.

    Args:
        blockchain: Mock blockchain state
        contract: Mock staking contract
        account: Test account information
    """
    # Give account sufficient balance for stake + gas
    blockchain.create_account(account["address"], Decimal("15.0"))

    # Stake tokens and mine some blocks to generate rewards
    stake_tokens(account["address"], Decimal("10.0"), blockchain, contract)

    # Mine more blocks to generate significant rewards
    for _ in range(100):  # Increase number of blocks
        blockchain.mine_block()

    # Record initial balance
    initial_balance = blockchain.get_account(account["address"]).balance

    # Get rewards amount before claiming
    position = get_staking_position_mock(account["address"], blockchain, contract)
    rewards_amount = position.unclaimed_rewards

    # Claim rewards
    result = contract.claim_rewards(account["address"])
    result = format_transaction(result)

    assert result["status"] == "success"
    assert result["hash"] is not None

    # Check balance increased by reward amount (minus gas)
    final_balance = blockchain.get_account(account["address"]).balance
    gas_cost = contract.gas_limit * blockchain.gas_price / Decimal("1000000000000000000")  # Convert wei to ETH

    # Use a more flexible comparison with relative tolerance
    expected_balance = initial_balance + rewards_amount - gas_cost
    logger.info(f"Expected balance: {expected_balance}, actual balance: {final_balance}, difference: {abs(final_balance - expected_balance)}")
    assert abs(final_balance - expected_balance) < Decimal("0.01")


def test_claim_no_rewards(blockchain: MockBlockchainState, contract: MockStakingContract, account: Dict[str, str]) -> None:
    """Test claiming with no rewards.

    Args:
        blockchain: Mock blockchain state
        contract: Mock staking contract
        account: Test account information
    """
    blockchain.create_account(account["address"], Decimal("10.0"))
    
    # Stake some tokens first so we have a stake
    stake_tokens(account["address"], Decimal("1.0"), blockchain, contract)
    
    with pytest.raises(ValueError, match="No rewards available"):
        claim_rewards(account["address"], blockchain, contract)
