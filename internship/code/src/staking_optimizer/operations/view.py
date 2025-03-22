"""View staking position operations.

This module provides functionality to view staking positions and related information.
"""

from decimal import Decimal
from typing import Dict, Optional, Union

from langchain_ritual_toolkit import RitualToolkit

from ..types import StakingPosition
from ..blockchain.mock_state import MockBlockchainState
from ..blockchain.mock_contract import MockStakingContract


def get_staking_position_mock(
    address: str,
    blockchain: MockBlockchainState,
    contract: MockStakingContract,
) -> StakingPosition:
    """Get staking position for an address using mock objects directly.
    
    This is a helper function for testing purposes.

    Args:
        address: Address to get position for
        blockchain: Mock blockchain state
        contract: Mock staking contract

    Returns:
        StakingPosition object with position details
    """
    return contract._get_staking_position_internal(address)


async def get_staking_position(
    address: str,
    toolkit: RitualToolkit,
) -> StakingPosition:
    """Get staking position for an address.

    Args:
        address: Address to get position for
        toolkit: RitualToolkit instance for blockchain interactions

    Returns:
        StakingPosition object with position details

    Raises:
        NotImplementedError: If not in mock mode
    """
    if not hasattr(toolkit.api, 'blockchain') or not hasattr(toolkit.api, 'contract'):
        raise NotImplementedError("get_staking_position is only implemented for mock mode")

    # Use mock contract's internal method to get position
    return toolkit.api.contract._get_staking_position_internal(address)


def format_position(position: StakingPosition) -> Dict[str, str]:
    """Format a staking position for display.

    Args:
        position: Position to format

    Returns:
        Dictionary with formatted position details
    """
    return {
        "address": position.address,
        "staked": f"{float(position.staked):.6f} ETH",
        "rewards": f"{float(position.rewards):.6f} ETH",
        "apr": f"{float(position.apr * 100):.1f}%",
        "previous_apr": f"{float(position.previous_apr * 100):.1f}%" if position.previous_apr else None,
    }
