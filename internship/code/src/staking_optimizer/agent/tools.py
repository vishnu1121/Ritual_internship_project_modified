"""Tools for StakeMate agent."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool, StructuredTool


class NoInput(BaseModel):
    """No input parameters."""
    pass


class AddressInput(BaseModel):
    """Input for address-based tools."""
    address: str = Field(description="Ethereum address")


class StakeArgs(BaseModel):
    """Input for staking tools."""
    address: str = Field(description="Ethereum address")
    amount: float = Field(description="Amount to stake in ETH")


def get_staking_tools(blockchain) -> List[BaseTool]:
    """Get staking tools."""
    def get_apr() -> str:
        """Get current staking APR."""
        return f"The current staking APR is {blockchain.get_staking_apr()}%"

    def stake(args: StakeArgs) -> str:
        """Stake ETH."""
        try:
            blockchain.stake(args.address, args.amount)
            return f"Successfully staked {args.amount} ETH from address {args.address}"
        except Exception as e:
            return f"Failed to stake: {str(e)}"

    def get_balance(address: str) -> str:
        """Get account balance in ETH."""
        try:
            balance = blockchain.get_balance(address)
            return f"Account {address} has {balance} ETH"
        except Exception as e:
            return f"Failed to get balance: {str(e)}"

    def get_gas_price() -> str:
        """Get current gas price in gwei."""
        try:
            gas = blockchain.get_gas_price()
            return f"Current gas price is {gas} gwei"
        except Exception as e:
            return f"Failed to get gas price: {str(e)}"

    def get_staking_info() -> str:
        """Get general staking information."""
        return """Here's what you need to know about ETH staking:

1. Requirements:
   - Minimum stake: 32 ETH for solo staking, or any amount for liquid staking
   - Must have enough ETH for gas fees
   - Need a reliable internet connection for validator duties

2. Benefits:
   - Earn staking rewards (current APR shown by GetStakingAPR tool)
   - Help secure the Ethereum network
   - Participate in network consensus

3. Risks:
   - Slashing risk if validator misbehaves
   - Price volatility of ETH
   - Smart contract risks

4. Steps to Start:
   1. Check your ETH balance
   2. Choose staking amount
   3. Execute stake transaction
   4. Monitor your position

Use other tools like GetBalance and GetGasPrice to check specific details."""

    return [
        StructuredTool(
            name="GetStakingAPR",
            description="Get current staking APR percentage",
            func=get_apr,
            args_schema=NoInput,
            return_direct=True
        ),
        StructuredTool(
            name="Stake",
            description="Stake ETH from an address. Requires address and amount in ETH.",
            func=stake,
            args_schema=StakeArgs,
            return_direct=True
        ),
        StructuredTool(
            name="GetBalance",
            description="Get account balance in ETH for an address",
            func=get_balance,
            args_schema=AddressInput,
            return_direct=True
        ),
        StructuredTool(
            name="GetGasPrice",
            description="Get current gas price in gwei",
            func=get_gas_price,
            args_schema=NoInput,
            return_direct=True
        ),
        StructuredTool(
            name="GetStakingInfo",
            description="Get general information about ETH staking",
            func=get_staking_info,
            args_schema=NoInput,
            return_direct=True
        )
    ]
