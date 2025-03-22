"""Tools for staking operations."""
from decimal import Decimal
from typing import Dict, List, Optional

from langchain_core.tools import BaseTool, StructuredTool, Tool
from pydantic import BaseModel, Field

from ...blockchain import MockBlockchainState, MockStakingContract
from ...operations import (
    get_staking_position_mock,
    stake_tokens,
    unstake_tokens,
    claim_rewards,
    format_position,
)
from ...utils import format_transaction


class StakeArgs(BaseModel):
    """Arguments for staking tokens."""
    address: str = Field(..., description="The address to stake tokens from")
    amount: Decimal = Field(..., description="Amount of tokens to stake in ETH")


class UnstakeArgs(BaseModel):
    """Arguments for unstaking tokens."""
    address: str = Field(..., description="The address to unstake tokens from")
    amount: Optional[Decimal] = Field(None, description="Amount of tokens to unstake in ETH. If None, unstakes all tokens.")


class ClaimArgs(BaseModel):
    """Arguments for claiming rewards."""
    address: str = Field(..., description="The address to claim rewards for")


class ViewArgs(BaseModel):
    """Arguments for viewing staking position."""
    address: str = Field(..., description="The address to view staking position for")


def create_staking_tools(
    blockchain: MockBlockchainState,
    contract: MockStakingContract,
) -> List[BaseTool]:
    """Create tools for staking operations.
    
    Args:
        blockchain: Mock blockchain state
        contract: Mock staking contract
        
    Returns:
        List of LangChain tools for staking operations
    """
    tools = []

    # View staking position
    tools.append(
        Tool(
            name="view_staking_position",
            description="View current staking position including balance, staked amount, rewards, and APR",
            func=lambda args: format_position(
                get_staking_position_mock(args.address, blockchain, contract)
            ),
            args_schema=ViewArgs,
        )
    )

    # Get APR
    tools.append(
        Tool(
            name="GetStakingAPR",
            description="Get the current staking APR. Returns APR as a percentage with 2 decimal places (e.g. '5.00%'). Input can be any string.",
            func=lambda _: (
                print(f"Raw APR: {contract.apr}, Type: {type(contract.apr)}, After multiply: {contract.apr * 100}") or
                f"{contract.apr * 100:.2f}%"
            ),  # Accept string input, format to 2 decimal places
        )
    )

    # Get gas price
    tools.append(
        Tool(
            name="GetGasPrice",
            description="Get the current gas price in gwei",
            func=lambda _: f"{float(blockchain.gas_price) / 1e9:.1f} gwei",  # Convert wei to gwei
        )
    )

    # Get account balance
    tools.append(
        Tool(
            name="GetAccountBalance",
            description="Get the balance of an Ethereum address",
            func=lambda address: f"{float(blockchain.get_balance(address)):.1f} ETH",
        )
    )

    # Stake tokens
    tools.append(
        StructuredTool(
            name="stake_tokens",
            description="Stake ETH tokens to earn rewards",
            args_schema=StakeArgs,
            func=lambda args: format_transaction(
                stake_tokens(args.address, args.amount, blockchain, contract=contract)
            ),
        )
    )

    # Stake tokens (alias)
    tools.append(
        StructuredTool(
            name="Stake",
            description="Stake ETH tokens to earn rewards",
            args_schema=StakeArgs,
            func=lambda args: format_transaction(
                stake_tokens(args.address, args.amount, blockchain, contract=contract)
            ),
        )
    )

    # Unstake tokens
    tools.append(
        StructuredTool(
            name="unstake_tokens",
            description="Unstake tokens and return them to your wallet",
            args_schema=UnstakeArgs,
            func=lambda args: format_transaction(
                unstake_tokens(args.address, args.amount, blockchain, contract=contract)
            ),
        )
    )

    # Claim rewards
    tools.append(
        StructuredTool(
            name="claim_rewards",
            description="Claim earned staking rewards",
            args_schema=ClaimArgs,
            func=lambda args: format_transaction(
                claim_rewards(args.address, blockchain, contract=contract)
            ),
        )
    )

    return tools
