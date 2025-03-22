"""Tools for the StakingOptimizer agent."""
from typing import List

from langchain_core.tools import BaseTool

from ...blockchain import MockBlockchainState, MockStakingContract
from ...safety import SafetyValidator
from .staking_tools import create_staking_tools
from .safety_tools import create_safety_tools
from .compound_tools import create_compound_tools


def get_staking_tools(
    blockchain: MockBlockchainState,
    contract: MockStakingContract,
    validator: SafetyValidator,
) -> List[BaseTool]:
    """Get all tools for the StakingOptimizer agent.
    
    Args:
        blockchain: Mock blockchain state
        contract: Mock staking contract
        validator: Safety validator instance
        
    Returns:
        List of all available tools for the agent
    """
    tools = []
    
    # Add staking tools
    tools.extend(create_staking_tools(blockchain, contract))
    
    # Add safety tools
    tools.extend(create_safety_tools(validator))
    
    # Add compound tools
    tools.extend(create_compound_tools(blockchain, contract))
    
    return tools


__all__ = ["get_staking_tools"]
