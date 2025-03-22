"""Tools for auto-compounding operations."""
from typing import Dict, List, Optional
from decimal import Decimal
from datetime import timedelta

from langchain_core.tools import BaseTool, StructuredTool, Tool
from pydantic import BaseModel, Field

from ...blockchain import MockBlockchainState, MockStakingContract
from ...autocompound import (
    AutoCompoundMonitor,
    ThresholdStrategy,
    TimeBasedStrategy,
    GasOptimizer
)


class CompoundArgs(BaseModel):
    """Arguments for compound operation."""
    address: str = Field(..., description="The address to compound rewards for")
    min_rewards: Optional[Decimal] = Field(None, description="Minimum rewards threshold to trigger compounding")
    max_gas_price: Optional[int] = Field(None, description="Maximum gas price to allow for compounding")


def create_compound_tools(
    blockchain: MockBlockchainState,
    contract: MockStakingContract,
) -> List[BaseTool]:
    """Create tools for auto-compounding operations.
    
    Args:
        blockchain: Mock blockchain state
        contract: Mock staking contract
        
    Returns:
        List of LangChain tools for auto-compounding
    """
    # Create components
    gas_optimizer = GasOptimizer(blockchain=blockchain)
    threshold_strategy = ThresholdStrategy(
        min_reward_threshold=Decimal("0.1"),  # 0.1 ETH minimum reward
        max_gas_price=Decimal("100"),  # 100 gwei max gas price
    )
    time_strategy = TimeBasedStrategy(
        compound_interval=timedelta(days=7),  # Compound weekly
        min_reward_threshold=Decimal("0.05"),  # 0.05 ETH minimum reward
        max_gas_price=Decimal("100"),  # 100 gwei max gas price
    )
    monitor = AutoCompoundMonitor(
        address="test_address",  # Will be overridden in tool calls
        strategy=threshold_strategy,  # Default to threshold strategy
        blockchain=blockchain,
        contract=contract,
    )

    tools = []

    # Check compound status
    tools.append(
        Tool(
            name="check_compound_status",
            description="Check if rewards should be compounded based on current conditions",
            func=lambda address: {
                "rewards": f"{float(monitor.contract.rewards[address]):.6f} ETH",
                "can_compound": str(monitor.check_rewards(address)).lower(),
            },
        )
    )

    # Execute compound
    tools.append(
        StructuredTool(
            name="execute_compound",
            description="Execute compound operation for an address",
            args_schema=CompoundArgs,
            func=lambda args: {
                "status": "success" if (result := monitor.execute_compound(
                    address=args.address,
                    blockchain=blockchain,
                    contract=contract,
                    min_rewards=args.min_rewards,
                    max_gas_price=args.max_gas_price,
                )) is not None else "failed",
                "value": result["value"] if result and "value" in result else "0.000000 ETH",
            },
        )
    )

    # Get compound stats
    tools.append(
        Tool(
            name="get_compound_stats",
            description="Get statistics about past compound operations",
            func=lambda address: {
                **monitor.get_compound_stats(address),
                "last_compound": (
                    monitor.compound_history[-1].timestamp.isoformat()
                    if monitor.compound_history
                    else None
                ),
            },
        )
    )

    return tools
