"""Common types used across the staking optimizer.

This module defines core data structures used throughout the staking optimizer
implementation. These types provide a consistent interface for representing
staking-related data across different components of the system.

Key Types:
    - StakingPosition: Represents a user's staking position including amount,
      rewards, and APR information
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Optional


@dataclass
class StakingPosition:
    """Represents a user's staking position and associated rewards.

    This class tracks all relevant information about a user's stake in the system,
    including the staked amount, unclaimed rewards, and current/previous APR rates.
    All numeric values are stored as Decimal to ensure precise financial calculations.

    Attributes:
        address: Staker's Ethereum address (0x-prefixed hex string)
        staked: Amount of ETH currently staked (as Decimal)
        rewards: Unclaimed rewards in ETH (as Decimal)
        apr: Current Annual Percentage Rate (as Decimal, e.g. 0.1 for 10%)
        previous_apr: Previous APR before last rate change (as Decimal or None)

    Properties:
        unclaimed_rewards: Alias for rewards to maintain API compatibility

    Notes:
        - All numeric inputs are converted to Decimal in post_init
        - APR is stored as a decimal (e.g. 0.1 for 10%) not a percentage
        - previous_apr is optional and only set when APR changes
    """

    address: str
    staked: Decimal
    rewards: Decimal
    apr: Decimal
    previous_apr: Optional[Decimal] = None

    @property
    def unclaimed_rewards(self) -> Decimal:
        """Get unclaimed rewards amount.
        
        This is an alias for the rewards field to maintain backwards compatibility
        with older code that expects the unclaimed_rewards property.

        Returns:
            Decimal: Amount of unclaimed rewards in ETH
        """
        return self.rewards

    def __post_init__(self):
        """Convert all numeric values to Decimal type.
        
        This ensures consistent decimal precision for all financial calculations
        by converting any non-Decimal numeric inputs to Decimal instances.
        """
        if not isinstance(self.staked, Decimal):
            self.staked = Decimal(str(self.staked))
        if not isinstance(self.rewards, Decimal):
            self.rewards = Decimal(str(self.rewards))
        if not isinstance(self.apr, Decimal):
            self.apr = Decimal(str(self.apr))
        if self.previous_apr is not None and not isinstance(self.previous_apr, Decimal):
            self.previous_apr = Decimal(str(self.previous_apr))
