"""Reward monitoring for auto-compound functionality.

This module provides reward monitoring capabilities to track staking rewards
and trigger auto-compounding based on configured strategies.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional

from ..blockchain import MockBlockchainState, MockStakingContract
from ..operations.stake import stake_tokens
from ..operations.view import get_staking_position_mock, StakingPosition
from ..utils import format_transaction
from .optimizer import GasOptimizer
from .strategy import AutoCompoundStrategy, CompoundDecision


logger = logging.getLogger(__name__)


@dataclass
class CompoundEvent:
    """Record of an auto-compound event.
    
    Attributes:
        timestamp: When the compound occurred
        rewards: Amount of rewards that were compounded
        gas_price: Gas price at time of compound
        gas_used: Gas used for the compound transaction
        transaction_hash: Hash of the compound transaction
        address: Address that was compounded
    """
    
    timestamp: datetime
    rewards: Decimal
    gas_price: Decimal
    gas_used: Decimal
    transaction_hash: str
    address: str

    @property
    def gas_cost(self) -> Decimal:
        """Calculate total gas cost."""
        return self.gas_price * self.gas_used


@dataclass
class RewardMonitor:
    """Monitors staking rewards and executes auto-compound strategies.
    
    This class tracks staking positions and their rewards, executing
    auto-compound strategies when conditions are favorable.
    
    Attributes:
        address: Address being monitored
        strategy: Auto-compound strategy to use
        blockchain: Mock blockchain state
        contract: Mock staking contract
        compound_history: Record of compound events
        last_check: Last time rewards were checked
    """
    
    address: str
    strategy: AutoCompoundStrategy
    blockchain: MockBlockchainState
    contract: MockStakingContract
    compound_history: List[CompoundEvent] = field(default_factory=list)
    last_check: Optional[datetime] = None
    gas_optimizer: GasOptimizer = field(init=False)
    
    def __post_init__(self):
        """Initialize gas optimizer."""
        self.gas_optimizer = GasOptimizer(
            blockchain=self.blockchain,
            window_size=60,  # Look at last hour
            min_window_size=5,  # Minimum 5 minute window
        )
    
    def check_rewards(self, address: Optional[str] = None) -> bool:
        """Check current rewards and decide whether to compound.
        
        Args:
            address: Optional address to check. If not provided, uses the monitor's address.
            
        Returns:
            True if rewards should be compounded, False otherwise
            
        Raises:
            KeyError: If address does not exist
        """
        # Use provided address or fall back to monitor's address
        check_address = address or self.address
        
        # Get current position
        position = get_staking_position_mock(
            check_address,
            self.blockchain,
            self.contract,
        )
        
        # Update last check time
        self.last_check = self.blockchain.last_block_time
        
        # Check if rewards are too small
        if position.rewards < self.strategy.min_reward_threshold:
            return False
            
        # Check if gas price is too high
        if not self.gas_optimizer.check_gas_price():
            return False
            
        # All checks passed
        return True

    def execute_compound(
        self,
        address: Optional[str] = None,
        blockchain: Optional[MockBlockchainState] = None,
        contract: Optional[MockStakingContract] = None,
        min_rewards: Optional[Decimal] = None,
        max_gas_price: Optional[int] = None,
    ) -> Optional[Dict[str, str]]:
        """Execute auto-compound for an address.

        Args:
            address: The address to auto-compound for. Defaults to monitor's address.
            blockchain: Mock blockchain state. Defaults to monitor's blockchain.
            contract: Mock staking contract. Defaults to monitor's contract.
            min_rewards: Minimum rewards required to auto-compound
            max_gas_price: Maximum gas price in wei to auto-compound at

        Returns:
            Dictionary with transaction details if successful, None otherwise
        """
        try:
            # Use provided values or fall back to instance variables
            check_address = address or self.address
            check_blockchain = blockchain or self.blockchain
            check_contract = contract or self.contract

            # Get current rewards and convert to Decimal
            rewards = check_contract.get_rewards(check_address)
            if not isinstance(rewards, Decimal):
                rewards = Decimal(str(rewards))

            # Convert and check minimum rewards
            if min_rewards is not None:
                if not isinstance(min_rewards, Decimal):
                    min_rewards = Decimal(str(min_rewards))
            else:
                min_rewards = self.strategy.min_reward_threshold

            if rewards < min_rewards:
                logger.info(
                    f"Insufficient rewards: {float(rewards):.1f} ETH < {float(min_rewards):.1f} ETH"
                )
                return None

            # Check gas price
            gas_price = check_blockchain.gas_price
            if max_gas_price is None:
                max_gas_price = self.strategy.max_gas_price

            if gas_price > max_gas_price:
                logger.info(
                    f"Gas price too high: {gas_price} wei > {max_gas_price} wei"
                )
                return None

            # Execute compound
            tx = check_contract.compound(check_address)
            tx_dict = format_transaction(tx)

            # Record compound event
            event = CompoundEvent(
                timestamp=check_blockchain.last_block_time,
                rewards=rewards,
                gas_price=gas_price,
                gas_used=Decimal("100000"),  # Standard gas usage
                transaction_hash=tx_dict["hash"],
                address=check_address,
            )
            self.compound_history.append(event)

            return tx_dict

        except Exception as e:
            logger.error(f"Auto-compound failed for {check_address}: {str(e)}")
            return None

    def execute_compound_v2(
        self,
        address: str,
        blockchain: MockBlockchainState,
        contract: MockStakingContract,
        min_rewards: Optional[Decimal] = None,
        max_gas_price: Optional[int] = None,
    ) -> Dict[str, str]:
        """Execute auto-compound for an address.

        Args:
            address: The address to auto-compound for
            blockchain: Mock blockchain state
            contract: Mock staking contract
            min_rewards: Minimum rewards required to auto-compound
            max_gas_price: Maximum gas price in wei to auto-compound at

        Returns:
            Dictionary with transaction details

        Raises:
            ValueError: If rewards are insufficient or gas price too high
        """
        try:
            # Get current rewards and convert to Decimal
            rewards = contract.get_rewards(address)
            if not isinstance(rewards, Decimal):
                rewards = Decimal(str(rewards))

            # Convert and check minimum rewards
            if min_rewards is not None:
                if not isinstance(min_rewards, Decimal):
                    min_rewards = Decimal(str(min_rewards))
                if rewards < min_rewards:
                    raise ValueError(
                        f"Insufficient rewards: {float(rewards):.1f} ETH < {float(min_rewards):.1f} ETH"
                    )

            # Check gas price
            gas_price = blockchain.gas_price
            if max_gas_price is not None and gas_price > max_gas_price:
                raise ValueError(
                    f"Gas price too high: {gas_price} wei > {max_gas_price} wei"
                )

            # Execute compound
            tx = contract.compound(address)
            return {"status": "success", "transaction_hash": tx["hash"] if isinstance(tx, dict) else tx.hash}

        except Exception as e:
            logger.error(f"Auto-compound failed for {address}: {str(e)}")
            return {"status": "failed", "error": str(e)}

    def get_compound_stats(self, address: Optional[str] = None) -> Dict[str, Decimal]:
        """Get statistics about auto-compound history.
        
        Args:
            address: Optional address to get stats for. If not provided, uses the monitor's address.
        
        Returns:
            Dictionary with:
            - total_compounds: Total number of compounds
            - total_rewards_compounded: Total rewards compounded
            - total_gas_cost: Total gas cost in wei
            - average_gas_cost: Average gas cost per compound
        """
        # Use provided address or fall back to monitor's address
        stats_address = address or self.address
        
        # Filter history for this address
        history = [e for e in self.compound_history if e.address == stats_address]
        
        if not history:
            return {
                "total_compounds": Decimal("0"),
                "total_rewards_compounded": Decimal("0"),
                "total_gas_cost": Decimal("0"),
                "average_gas_cost": Decimal("0"),
            }
            
        total_rewards = sum(e.rewards for e in history)
        total_gas = sum(e.gas_cost for e in history)
        
        return {
            "total_compounds": Decimal(len(history)),
            "total_rewards_compounded": total_rewards,
            "total_gas_cost": total_gas,
            "average_gas_cost": total_gas / len(history),
        }
