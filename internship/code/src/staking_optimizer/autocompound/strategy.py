"""Auto-compound strategies for staking rewards.

This module defines the interface and implementations for auto-compound strategies.
Each strategy determines when and how to compound staking rewards based on
different optimization criteria.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional

from staking_optimizer.blockchain.mock_state import MockBlockchainState
from staking_optimizer.operations.view import StakingPosition


@dataclass
class CompoundDecision:
    """Decision about whether to compound rewards.
    
    Attributes:
        should_compound: Whether rewards should be compounded
        reason: Explanation for the decision
        gas_price_threshold: Maximum gas price willing to pay
        min_reward_threshold: Minimum reward amount needed
    """
    
    should_compound: bool
    reason: str
    gas_price_threshold: Optional[Decimal] = None
    min_reward_threshold: Optional[Decimal] = None


class AutoCompoundStrategy(ABC):
    """Base class for auto-compound strategies.
    
    This abstract class defines the interface that all auto-compound strategies
    must implement. Strategies determine when it's optimal to compound rewards
    based on various factors like gas prices, reward amounts, and time intervals.
    """
    
    @abstractmethod
    def should_compound(
        self,
        position: StakingPosition,
        blockchain: MockBlockchainState,
    ) -> CompoundDecision:
        """Determine if rewards should be compounded.
        
        Args:
            position: Current staking position
            blockchain: Blockchain state for gas prices etc.
            
        Returns:
            CompoundDecision with compound recommendation and reasoning
        """
        pass


class ThresholdStrategy(AutoCompoundStrategy):
    """Strategy that compounds when rewards reach a threshold.
    
    This strategy compounds rewards when they reach a minimum threshold that
    makes the gas costs worthwhile.
    
    Attributes:
        min_reward_threshold: Minimum reward amount to trigger compounding
        max_gas_price: Maximum gas price willing to pay
    """
    
    def __init__(
        self,
        min_reward_threshold: Decimal,
        max_gas_price: Decimal,
    ) -> None:
        """Initialize threshold strategy.
        
        Args:
            min_reward_threshold: Minimum reward amount to trigger compounding
            max_gas_price: Maximum gas price willing to pay
        """
        self.min_reward_threshold = min_reward_threshold
        self.max_gas_price = max_gas_price
        
    def set_threshold(self, threshold: Decimal) -> None:
        """Set minimum reward threshold.
        
        Args:
            threshold: New minimum reward threshold
        """
        self.min_reward_threshold = threshold

    def set_gas_threshold(self, threshold: Decimal) -> None:
        """Set maximum gas price threshold.
        
        Args:
            threshold: New maximum gas price threshold
        """
        self.max_gas_price = threshold

    def should_compound(
        self,
        position: StakingPosition,
        blockchain: MockBlockchainState,
    ) -> CompoundDecision:
        """Determine if rewards should be compounded based on thresholds.
        
        Compounds when rewards exceed threshold and gas price is acceptable.
        
        Args:
            position: Current staking position
            blockchain: Blockchain state for gas prices
            
        Returns:
            CompoundDecision with threshold-based recommendation
        """
        current_gas = blockchain.get_gas_price()
        
        # Check if gas price is too high
        if current_gas > self.max_gas_price:
            return CompoundDecision(
                should_compound=False,
                reason=f"Gas price ({current_gas} gwei) exceeds threshold ({self.max_gas_price} gwei)",
                gas_price_threshold=self.max_gas_price,
                min_reward_threshold=self.min_reward_threshold
            )
            
        # Check if rewards are too low
        if position.rewards < self.min_reward_threshold:
            return CompoundDecision(
                should_compound=False,
                reason=f"Rewards ({position.rewards} ETH) below threshold ({self.min_reward_threshold} ETH)",
                gas_price_threshold=self.max_gas_price,
                min_reward_threshold=self.min_reward_threshold
            )
            
        # All conditions met
        return CompoundDecision(
            should_compound=True,
            reason=f"Rewards ({position.rewards} ETH) exceed threshold ({self.min_reward_threshold} ETH) and gas price ({current_gas} gwei) is acceptable",
            gas_price_threshold=self.max_gas_price,
            min_reward_threshold=self.min_reward_threshold
        )


class TimeBasedStrategy(AutoCompoundStrategy):
    """Strategy that compounds at regular time intervals.
    
    This strategy compounds rewards on a fixed schedule as long as gas prices
    are reasonable and there are sufficient rewards.
    
    Attributes:
        compound_interval: Time between compounding
        min_reward_threshold: Minimum reward amount to compound
        max_gas_price: Maximum gas price willing to pay
        last_compound: Time of last compound
    """
    
    def __init__(
        self,
        compound_interval: timedelta,
        min_reward_threshold: Decimal,
        max_gas_price: Decimal,
    ) -> None:
        """Initialize time-based strategy.
        
        Args:
            compound_interval: Time between compounding
            min_reward_threshold: Minimum reward amount to compound
            max_gas_price: Maximum gas price willing to pay
        """
        self.compound_interval = compound_interval
        self.min_reward_threshold = min_reward_threshold
        self.max_gas_price = max_gas_price
        self.last_compound: Optional[datetime] = None
        
    def should_compound(
        self,
        position: StakingPosition,
        blockchain: MockBlockchainState,
    ) -> CompoundDecision:
        """Determine if rewards should be compounded based on time interval.
        
        Compounds when enough time has passed and conditions are favorable.
        
        Args:
            position: Current staking position
            blockchain: Blockchain state for gas prices and time
            
        Returns:
            CompoundDecision with time-based recommendation
        """
        current_time = blockchain.last_block_time
        current_gas = blockchain.gas_price
        
        # Check gas price first
        if current_gas > self.max_gas_price:
            return CompoundDecision(
                should_compound=False,
                reason=(
                    f"Gas price {current_gas} exceeds maximum {self.max_gas_price}"
                ),
                gas_price_threshold=self.max_gas_price,
            )
            
        # Check minimum rewards
        if position.rewards < self.min_reward_threshold:
            return CompoundDecision(
                should_compound=False,
                reason=(
                    f"Rewards {position.rewards} below threshold "
                    f"{self.min_reward_threshold}"
                ),
                min_reward_threshold=self.min_reward_threshold,
            )
            
        # If first time or enough time has passed
        if (
            self.last_compound is None
            or current_time - self.last_compound >= self.compound_interval
        ):
            self.last_compound = current_time
            return CompoundDecision(
                should_compound=True,
                reason=(
                    f"Time interval {self.compound_interval} reached with "
                    f"favorable conditions"
                ),
                gas_price_threshold=self.max_gas_price,
                min_reward_threshold=self.min_reward_threshold,
            )
            
        time_remaining = (
            self.last_compound + self.compound_interval - current_time
        )
        return CompoundDecision(
            should_compound=False,
            reason=f"Waiting {time_remaining} until next compound interval",
        )


class GasOptimizedStrategy(AutoCompoundStrategy):
    """Strategy that optimizes for gas prices.
    
    This strategy tracks gas price trends and compounds when gas prices are
    favorable relative to recent history.
    
    Attributes:
        gas_percentile: Target gas price percentile (lower is more aggressive)
        min_reward_threshold: Minimum reward amount to compound
        max_gas_price: Maximum gas price willing to pay
        gas_window: Number of blocks to consider for gas trends
    """
    
    def __init__(
        self,
        gas_percentile: float = 25.0,
        min_reward_threshold: Decimal = Decimal("0.1"),
        max_gas_price: Decimal = Decimal("100"),
        gas_window: int = 100,
    ) -> None:
        """Initialize gas-optimized strategy.
        
        Args:
            gas_percentile: Target gas price percentile (0-100)
            min_reward_threshold: Minimum reward amount to compound
            max_gas_price: Maximum gas price willing to pay
            gas_window: Number of blocks to consider for gas trends
        """
        if not 0 <= gas_percentile <= 100:
            raise ValueError("gas_percentile must be between 0 and 100")
            
        self.gas_percentile = gas_percentile
        self.min_reward_threshold = min_reward_threshold
        self.max_gas_price = max_gas_price
        self.gas_window = gas_window
        self.recent_gas_prices: list[Decimal] = []
        
    def should_compound(
        self,
        position: StakingPosition,
        blockchain: MockBlockchainState,
    ) -> CompoundDecision:
        """Determine if rewards should be compounded based on gas optimization.
        
        Compounds when gas prices are favorable compared to recent history.
        
        Args:
            position: Current staking position
            blockchain: Blockchain state for gas prices
            
        Returns:
            CompoundDecision with gas-optimized recommendation
        """
        current_gas = blockchain.gas_price
        
        # Update gas price history
        self.recent_gas_prices.append(current_gas)
        if len(self.recent_gas_prices) > self.gas_window:
            self.recent_gas_prices.pop(0)
            
        # Not enough history yet
        if len(self.recent_gas_prices) < self.gas_window:
            return CompoundDecision(
                should_compound=False,
                reason=(
                    f"Building gas price history: "
                    f"{len(self.recent_gas_prices)}/{self.gas_window} blocks"
                ),
            )
            
        # Check minimum rewards
        if position.rewards < self.min_reward_threshold:
            return CompoundDecision(
                should_compound=False,
                reason=(
                    f"Rewards {position.rewards} below threshold "
                    f"{self.min_reward_threshold}"
                ),
                min_reward_threshold=self.min_reward_threshold,
            )
            
        # Calculate gas price threshold from history
        sorted_prices = sorted(self.recent_gas_prices)
        threshold_index = int(len(sorted_prices) * self.gas_percentile / 100)
        gas_threshold = sorted_prices[threshold_index]
        
        # Cap threshold at max_gas_price
        gas_threshold = min(gas_threshold, self.max_gas_price)
        
        if current_gas > gas_threshold:
            return CompoundDecision(
                should_compound=False,
                reason=(
                    f"Waiting for gas price {current_gas} to drop below "
                    f"{gas_threshold}"
                ),
                gas_price_threshold=gas_threshold,
            )
            
        return CompoundDecision(
            should_compound=True,
            reason=(
                f"Gas price {current_gas} below {self.gas_percentile}th "
                f"percentile {gas_threshold}"
            ),
            gas_price_threshold=gas_threshold,
            min_reward_threshold=self.min_reward_threshold,
        )
