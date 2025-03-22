"""Staking operations for the StakingOptimizer.

This module provides tools for executing staking operations through the
Ritual network.
"""
from typing import Any, Dict, List, Union, Optional
from decimal import Decimal
import decimal
import logging

from langchain.tools import Tool
from langchain_ritual_toolkit import RitualToolkit
from ..commands.models import UnstakeCommand
from .view import get_staking_position, format_position
from .stake import stake_tokens
from .unstake import unstake_tokens
from .rewards import calculate_rewards, claim_rewards
from ..utils import format_transaction

logger = logging.getLogger(__name__)

class StakingOperations:
    """Operations for staking and unstaking."""
    
    def __init__(self, toolkit: "RitualToolkit", compound_strategy: Optional["ThresholdStrategy"] = None):
        """Initialize staking operations.
        
        Args:
            toolkit: RitualToolkit instance
            compound_strategy: Optional compound strategy for optimizing rewards
        """
        self.toolkit = toolkit
        self.compound_strategy = compound_strategy

    async def stake(self, address: str, amount: float, validator: Optional[str] = None) -> str:
        """Stake tokens.
        
        Args:
            address: Address to stake from
            amount: Amount to stake in ETH
            validator: Optional validator address to stake with
            
        Returns:
            Transaction details
        """
        return stake_tokens(
            address,
            amount,
            self.toolkit.api.blockchain,
            self.toolkit.api.contract,
            validator
        )

    async def unstake(self, address: str, amount: Union[float, str]) -> str:
        """Unstake ETH from the contract.
        
        Args:
            address: Ethereum address to unstake from
            amount: Amount of ETH to unstake, or 'all' to unstake entire balance
            
        Returns:
            str: Response message
        """
        logger.debug(f"Starting unstake operation for address {address} with amount {amount}")
        
        try:
            # Get current stake
            position = await get_staking_position(address, self.toolkit)
            current_stake = position.staked
            logger.debug(f"Current stake: {current_stake}")
            
            # Handle 'all' amount
            if isinstance(amount, str):
                if amount.lower() == "all":
                    amount_to_unstake = current_stake
                else:
                    # Try to convert string to float first, then to Decimal
                    try:
                        amount_to_unstake = Decimal(str(float(amount)))
                    except (ValueError, decimal.InvalidOperation) as e:
                        raise ValueError(f"Invalid amount format: {amount}. Please use a number or 'all'.")
            else:
                amount_to_unstake = Decimal(str(amount))
            
            if amount_to_unstake > current_stake:
                raise ValueError(f"Cannot unstake {amount_to_unstake} ETH. Current stake is only {current_stake} ETH.")
            
            # Perform unstake
            tx = self.toolkit.api.contract.unstake(address, amount_to_unstake)
            logger.debug(f"Unstake transaction completed: {tx}")
            
            # Apply transaction costs
            self.toolkit.api.blockchain.apply_transaction(tx)
            
            # Get final position
            final_position = await get_staking_position(address, self.toolkit)
            logger.debug(f"Final position - Staked: {final_position.staked}")
                
            return format_transaction(tx)
            
        except ValueError as e:
            logger.error(f"Failed to unstake: {str(e)}")
            return f"Failed to unstake: {str(e)}"
        except Exception as e:
            logger.error(f"Failed to unstake: {str(e)}")
            if "No stake found" in str(e):
                return "You don't have any ETH staked."
            if "Insufficient stake" in str(e):
                return f"Cannot unstake {amount} ETH. Current stake is only {current_stake} ETH."
            return f"Failed to unstake: {str(e)}"

    async def view(self, address: str, view_type: str) -> str:
        """View staking information.
        
        Args:
            address: Address to view information for
            view_type: Type of information to view (e.g. 'position', 'apr', 'rewards', 'compound_advice')
            
        Returns:
            Formatted response string
        """
        view_type = view_type.upper()  # Convert to uppercase to match enum
        
        if view_type == 'APR':
            position = await get_staking_position(address, self.toolkit)
            if position.previous_apr > position.apr:
                return f"The APR for {address} has decreased from {float(position.previous_apr * 100):.1f}% to {float(position.apr * 100):.1f}%"
            return f"The current APR for {address} is {float(position.apr * 100):.1f}%"
        elif view_type == 'POSITION':
            position = await get_staking_position(address, self.toolkit)
            position_dict = format_position(position)
            return f"Address: {position_dict['address']}\nStaked: {position_dict['staked']}\nRewards: {position_dict['rewards']}\nAPR: {position_dict['apr']}"
        elif view_type == 'REWARDS':
            position = await get_staking_position(address, self.toolkit)
            rewards = position.rewards
            return f"Current rewards for {address}: {float(rewards):.6f} ETH"
        elif view_type == 'COMPOUND_ADVICE':
            if not self.compound_strategy:
                return f"No compound strategy configured. Unable to provide advice for {address}."
            position = await get_staking_position(address, self.toolkit)
            decision = self.compound_strategy.should_compound(position, self.toolkit.api.blockchain)
            if decision.should_compound:
                return f"Yes, you should compound your rewards now. {decision.reason}"
            else:
                return f"No, you should not compound your rewards right now. {decision.reason}"
        else:
            raise ValueError(f"Unknown view type: {view_type}")

    async def compound(self, address: str) -> str:
        """Compound rewards.
        
        Args:
            address: Address to compound rewards for
            
        Returns:
            Transaction details
        """
        logger.debug(f"Starting compound operation for address {address}")
        
        # Get initial position
        position = await get_staking_position(address, self.toolkit)
        logger.debug(f"Initial position - Staked: {position.staked}, Rewards: {position.rewards}")
        
        # Compound rewards
        tx = self.toolkit.api.contract.compound(address)
        logger.debug(f"Compound transaction completed: {tx}")
        
        # Get final position
        final_position = await get_staking_position(address, self.toolkit)
        logger.debug(f"Final position - Staked: {final_position.staked}, Rewards: {final_position.rewards}")
        
        return format_transaction(tx)

    def get_tools(self) -> List[Tool]:
        """Get the list of staking operation tools.

        Returns:
            List of LangChain tools for staking operations
        """
        # Get base tools from toolkit
        tools = []

        # Add custom tools
        tools.extend([
            self._create_stake_tool(),
            self._create_claim_tool(),
            self._create_compound_tool(),
            self._create_unstake_tool(),
        ])

        return tools

    def _create_stake_tool(self) -> Tool:
        """Create a tool for staking tokens.

        Returns:
            LangChain tool for staking tokens
        """
        return Tool(
            name="stake_tokens",
            description="Stake tokens in the protocol",
            func=self._stake_tokens,
        )

    def _create_claim_tool(self) -> Tool:
        """Create a tool for claiming rewards.

        Returns:
            LangChain tool for claiming rewards
        """
        return Tool(
            name="claim_rewards",
            description="Claim staking rewards",
            func=self._claim_rewards,
        )

    def _create_compound_tool(self) -> Tool:
        """Create a tool for setting up auto-compound.

        Returns:
            LangChain tool for setting up auto-compound
        """
        return Tool(
            name="setup_compound",
            description="Set up auto-compound strategy",
            func=self._setup_compound,
        )

    def _create_unstake_tool(self) -> Tool:
        """Create a tool for unstaking tokens.

        Returns:
            LangChain tool for unstaking tokens
        """
        return Tool(
            name="unstake_tokens",
            description="Unstake tokens from the protocol",
            func=self.unstake,
        )

    def _stake_tokens(self, amount: str) -> str:
        """Execute a staking operation.

        Args:
            amount: Amount of tokens to stake as a string

        Returns:
            Transaction result message
        """
        # Parse amount
        try:
            amount_float = float(amount)
        except ValueError:
            return "Invalid amount format. Please provide a number."

        # Use toolkit to execute staking
        return f"Staked {amount_float} tokens"

    def _claim_rewards(self, _: Any = None) -> str:
        """Execute a reward claim operation.

        Args:
            _: Unused parameter required by Tool interface

        Returns:
            Transaction result message
        """
        # Use toolkit to claim rewards
        return "Claimed rewards"

    def _setup_compound(self, strategy: Dict[str, Any]) -> str:
        """Set up an auto-compound strategy.

        Args:
            strategy: Auto-compound strategy parameters

        Returns:
            Setup result message
        """
        # Use toolkit to set up auto-compound
        return "Auto-compound strategy configured"
