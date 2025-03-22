"""Reward calculation and claiming operations.

This module provides functionality for calculating and claiming staking rewards.
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Dict

from ..blockchain import MockBlockchainState, MockStakingContract
from ..utils import format_transaction


@dataclass
class RewardInfo:
    """Information about staking rewards.

    Attributes:
        address: User's address
        unclaimed_rewards: Current unclaimed rewards
        apr: Current staking APR
        projected_daily: Projected daily rewards at current rate
        projected_monthly: Projected monthly rewards at current rate
        projected_yearly: Projected yearly rewards at current rate
    """

    address: str
    unclaimed_rewards: Decimal
    apr: Decimal
    projected_daily: Decimal
    projected_monthly: Decimal
    projected_yearly: Decimal


def calculate_rewards(
    address: str,
    blockchain: MockBlockchainState,
    contract: MockStakingContract,
) -> RewardInfo:
    """Calculate current and projected rewards for an address.

    Args:
        address: The address to calculate rewards for
        blockchain: Mock blockchain state
        contract: Mock staking contract

    Returns:
        RewardInfo with current and projected rewards

    Raises:
        KeyError: If address does not exist
    """
    # Get staking position and rewards
    position = contract.get_position(address)
    if not position:
        raise KeyError(f"No staking position found for {address}")

    # Calculate projected rewards
    daily = position.staked * position.apr / Decimal("365")
    monthly = daily * Decimal("30")
    yearly = daily * Decimal("365")

    return RewardInfo(
        address=address,
        unclaimed_rewards=position.rewards,
        apr=position.apr,
        projected_daily=daily,
        projected_monthly=monthly,
        projected_yearly=yearly,
    )


def claim_rewards(
    address: str,
    blockchain: MockBlockchainState,
    contract: MockStakingContract,
) -> Dict[str, str]:
    """Claim rewards for an address.

    Args:
        address: The address claiming rewards
        blockchain: Mock blockchain state
        contract: Mock staking contract

    Returns:
        Dictionary with transaction details

    Raises:
        ValueError: If no rewards available
        KeyError: If address does not exist
    """
    # Get current rewards
    position = contract.get_position(address)
    if not position:
        raise KeyError(f"No staking position found for {address}")

    if position.rewards == 0:
        raise ValueError("No rewards available")

    # Claim rewards
    tx = contract.claim_rewards(address)
    return format_transaction(tx)
