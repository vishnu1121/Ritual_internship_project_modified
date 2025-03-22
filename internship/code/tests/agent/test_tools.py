"""Tests for StakeMate tools."""

import pytest
from typing import List
from langchain_core.tools import BaseTool
from src.staking_optimizer.agent.tools import get_staking_tools
from src.staking_optimizer.agent.tools.staking_tools import StakeArgs, UnstakeArgs, ClaimArgs
from src.staking_optimizer.blockchain.mock_state import MockBlockchainState
from decimal import Decimal


@pytest.fixture
def blockchain() -> MockBlockchainState:
    """Provide a blockchain instance for tests.

    Args:
        None

    Returns:
        MockBlockchainState: A mock blockchain state instance.
    """
    return MockBlockchainState()


@pytest.fixture
def contract(blockchain: MockBlockchainState):
    """Provide a mock staking contract for tests.

    Args:
        blockchain: The mock blockchain instance.

    Returns:
        MockStakingContract: A mock staking contract instance.
    """
    from src.staking_optimizer.blockchain.mock_contract import MockStakingContract
    return MockStakingContract(blockchain)


@pytest.fixture
def validator():
    """Provide a safety validator for tests.

    Returns:
        SafetyValidator: A safety validator instance.
    """
    from src.staking_optimizer.validator.safety_validator import SafetyValidator
    return SafetyValidator()


@pytest.fixture
def tools(blockchain: MockBlockchainState, contract, validator) -> List[BaseTool]:
    """Provide tools instance for tests.

    Args:
        blockchain: The mock blockchain instance.
        contract: The mock staking contract.
        validator: The safety validator.

    Returns:
        List[BaseTool]: List of staking tools initialized with the mock blockchain.
    """
    return get_staking_tools(blockchain, contract, validator)


def test_tool_creation(tools: List[BaseTool]) -> None:
    """Tests that the staking tools are created with correct properties.

    Args:
        tools: List of staking tools to test.

    Returns:
        None

    Raises:
        AssertionError: If tools are not created correctly.
    """
    # We expect 12 tools total:
    # 4 staking tools: view_staking_position, stake_tokens, unstake_tokens, claim_rewards
    # 1 safety tool: validate_request
    # 3 compound tools: check_compound_status, execute_compound, get_compound_stats
    # 4 utility tools: GetStakingAPR, GetGasPrice, GetAccountBalance, Stake
    assert len(tools) == 12
    tool_names = {t.name for t in tools}
    expected_names = {
        "view_staking_position",
        "stake_tokens",
        "unstake_tokens",
        "claim_rewards",
        "validate_request",
        "check_compound_status",
        "execute_compound",
        "get_compound_stats",
        "GetStakingAPR",
        "GetGasPrice",
        "GetAccountBalance",
        "Stake"
    }
    assert tool_names == expected_names


def test_apr_tool(tools: List[BaseTool]) -> None:
    """Tests that the APR tool returns valid staking APR.

    Args:
        tools: List of staking tools to test.

    Returns:
        None

    Raises:
        AssertionError: If APR is not returned as expected.
    """
    apr_tool = next(t for t in tools if t.name == "GetStakingAPR")
    
    # Should return APR as string
    apr = apr_tool.invoke("get apr")
    assert isinstance(apr, str)
    # Convert percentage string to float
    apr_value = float(apr.rstrip("%"))
    assert isinstance(apr_value, float)
    assert 0 <= apr_value <= 100


def test_stake_tool(blockchain: MockBlockchainState, tools: List[BaseTool]) -> None:
    """Tests that the stake tool correctly processes ETH staking.

    Args:
        blockchain: The mock blockchain instance.
        tools: List of staking tools to test.

    Returns:
        None

    Raises:
        AssertionError: If staking operation does not work as expected.
    """
    stake_tool = next(t for t in tools if t.name == "Stake")
    test_address = "0x123"
    initial_balance = 10.0
    stake_amount = 1.0

    # Setup test account
    blockchain.create_account(test_address, balance=initial_balance)
    
    # Stake ETH
    args = StakeArgs(address=test_address, amount=Decimal(str(stake_amount)))
    result = stake_tool.func(args)
    assert isinstance(result, dict)
    assert "hash" in result
    tx_hash = result["hash"]
    assert isinstance(tx_hash, str)
    assert len(tx_hash) >= 42  # Minimum length for a valid Ethereum hash (0x + 40 chars)
    
    # Verify balance changed
    new_balance = float(blockchain.get_balance(test_address))
    expected_balance = initial_balance - stake_amount - 0.002  # Approximate gas cost
    assert abs(new_balance - expected_balance) < 0.005  # Use higher tolerance for gas cost variations


def test_balance_tool(blockchain: MockBlockchainState, tools: List[BaseTool]) -> None:
    """Tests that the balance tool correctly returns account balance.

    Args:
        blockchain: The mock blockchain instance.
        tools: List of staking tools to test.

    Returns:
        None

    Raises:
        AssertionError: If balance is not returned as expected.
    """
    balance_tool = next(t for t in tools if t.name == "GetAccountBalance")
    test_address = "0x123"
    initial_balance = 10.0

    # Setup test account
    blockchain.create_account(test_address, balance=initial_balance)
    
    # Get balance
    balance = balance_tool.invoke({
        "address": test_address
    })
    assert isinstance(balance, str)
    assert balance.endswith(" ETH")
    balance_value = float(balance.rstrip(" ETH"))
    assert balance_value == initial_balance


def test_gas_price_tool(tools: List[BaseTool]) -> None:
    """Tests that the gas price tool returns valid gas price.

    Args:
        tools: List of staking tools to test.

    Returns:
        None

    Raises:
        AssertionError: If gas price is not returned as expected.
    """
    gas_tool = next(t for t in tools if t.name == "GetGasPrice")
    
    # Get gas price
    gas_price = gas_tool.invoke("get gas price")  # Provide a dummy input string
    assert isinstance(gas_price, str)
    assert gas_price.endswith(" gwei")
    gas_price_value = float(gas_price.rstrip(" gwei"))
    assert gas_price_value > 0
