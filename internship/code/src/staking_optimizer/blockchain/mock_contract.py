"""Mock staking contract implementation for testing.

This module provides a simplified staking contract implementation for testing purposes.
It simulates an Ethereum staking contract with the following features:
    - ETH staking with minimum and maximum limits
    - Reward accrual based on stake amount and time
    - Partial and full unstaking
    - Reward claiming
    - Gas cost simulation

The implementation prioritizes simplicity and testability while maintaining realistic
blockchain behavior. It is designed to work with MockBlockchainState for end-to-end
testing of staking strategies.

Key Features:
    - Configurable min/max stake amounts
    - APR-based reward calculation
    - Transaction gas cost simulation
    - Nonce tracking for each staker
    - Detailed error messages for invalid operations

Typical usage example:
    blockchain = MockBlockchainState()
    contract = MockStakingContract(blockchain)
    tx = contract.stake("0xuser", Decimal("1.0"))
"""
import logging
from decimal import Decimal
from logging import getLogger
from typing import Dict, Optional

from ..types import StakingPosition
from .mock_state import MockBlockchainState
from .mock_transaction import MockTransaction

logger = getLogger(__name__)


class MockStakingContract:
    """Mock staking contract for testing.

    This contract simulates an Ethereum staking contract that allows users to stake ETH
    and earn rewards based on the amount staked and time (blocks) passed. It implements
    core staking functionality while maintaining realistic blockchain behavior.

    The contract follows these key principles:
    1. Fail-fast with clear errors - invalid operations raise descriptive exceptions
    2. Realistic behavior - simulates gas costs and blockchain mechanics
    3. Deterministic - operations have predictable outcomes for testing
    4. Safe operations - checks balances and limits before any state changes

    Attributes:
        address: Contract's Ethereum address (0x-prefixed hex string)
        blockchain: Reference to mock blockchain state
        min_stake: Minimum stake amount in ETH (default: 0.1)
        max_stake: Maximum stake amount in ETH (default: 1000.0)
        stakes: Mapping of staker address to staked amount in ETH
        rewards: Mapping of staker address to unclaimed rewards in ETH
        apr: Annual Percentage Rate for staking rewards (e.g. 0.1 for 10%)
        stake_block: Mapping of staker address to block number when stake was made
        nonces: Mapping of staker address to transaction nonce

    Raises:
        ValueError: If attempting an invalid operation (e.g. insufficient stake)
        KeyError: If attempting to access a nonexistent staker
    """

    GAS_LIMIT = 21000  # Standard gas limit for basic operations

    def __init__(self, blockchain: MockBlockchainState, address: str = "0x0") -> None:
        """Initialize mock staking contract.

        Args:
            blockchain: Mock blockchain state
            address: Contract address
        """
        self.blockchain = blockchain
        self.address = address
        self.stakes: Dict[str, Decimal] = {}  # Mapping of staker address to staked amount
        self.stake_block: Dict[str, int] = {}  # Mapping of staker address to block number when stake was made
        self.rewards: Dict[str, Decimal] = {}  # Mapping of staker address to unclaimed rewards
        self.min_stake = Decimal("0.1")  # Minimum 0.1 ETH stake
        self.max_stake = Decimal("100.0")  # Maximum 100 ETH stake
        self.gas_limit = 21000  # Standard gas limit for transactions
        self.apr: Decimal = Decimal("0.05")  # Fixed 5% APR
        self._previous_apr: Decimal = Decimal("0.05")  # Previous APR value
        self.nonces: Dict[str, int] = {}  # Track nonces per account
        
        # Create contract account in blockchain state
        if self.address not in self.blockchain.accounts:
            self.blockchain.create_account(self.address, float(1000))  # Give contract some ETH

        logger.info("Initialized MockStakingContract with address %s", self.address)

    def _get_staking_position_internal(self, address: str) -> StakingPosition:
        """Get staking position for an address.

        Args:
            address: Address to get position for

        Returns:
            StakingPosition object with current position details
        """
        staked = self.stakes.get(address, Decimal("0"))
        rewards = self.get_rewards(address)

        return StakingPosition(
            address=address,
            staked=staked,
            rewards=rewards,
            apr=self.apr,
            previous_apr=self._previous_apr
        )

    def get_position(self, address: str) -> StakingPosition:
        """Get staking position for an address.

        Args:
            address: Address to get position for

        Returns:
            StakingPosition object with current position details
        """
        return self._get_staking_position_internal(address)

    def _get_next_nonce(self, address: str) -> int:
        """Get next nonce for an address.

        Args:
            address: The address to get nonce for

        Returns:
            Next nonce value
        """
        if address not in self.nonces:
            self.nonces[address] = 0
        nonce = self.nonces[address]
        self.nonces[address] += 1
        return nonce

    def stake(self, address: str, amount: Decimal, validator: Optional[str] = None) -> MockTransaction:
        """Stake tokens in the contract.

        Args:
            address: Address staking tokens
            amount: Amount to stake
            validator: Optional validator address to stake with

        Returns:
            Transaction details

        Raises:
            ValueError: If amount is invalid or balance insufficient
            KeyError: If address does not exist
        """
        if amount < self.min_stake:
            raise ValueError(f"Minimum stake is {self.min_stake} ETH")
        if amount > self.max_stake:
            raise ValueError(f"Maximum stake is {self.max_stake} ETH")

        gas_cost = self._calculate_gas_cost()
        account = self.blockchain.get_account(address)
        logger.debug(f"Stake - Initial balance: {account.balance}, Initial staked: {account.staked_amount}")
        logger.debug(f"Stake - Amount: {amount}, Gas cost: {gas_cost}")

        # Create transaction
        tx = MockTransaction(
            from_address=address,
            to_address=self.address,
            value=amount,
            gas_limit=self.gas_limit,
            gas_price=self.blockchain.gas_price,
            nonce=self._get_next_nonce(address)
        )

        # Apply transaction to blockchain state
        tx.confirm()
        self.blockchain.apply_transaction(tx)

        # Update stakes after transaction is successful
        if address in self.stakes:
            self.stakes[address] = self.stakes[address] + amount
        else:
            self.stakes[address] = amount
        self.stake_block[address] = self.blockchain.current_block

        logger.debug(f"Stake - Updated stakes: {self.stakes}")
        return tx

    def unstake(self, address: str, amount: Decimal) -> MockTransaction:
        """Unstake tokens from the contract.

        Args:
            address: Address unstaking tokens
            amount: Amount to unstake

        Returns:
            Transaction details
        """
        if address not in self.stakes:
            raise ValueError("No stake found")

        staked_amount = self.stakes[address]
        if amount > staked_amount:
            raise ValueError("Insufficient stake")

        gas_cost = self._calculate_gas_cost()
        account = self.blockchain.get_account(address)
        staked = self.stakes.get(address, Decimal("0"))
        logger.debug(f"Unstake - Initial balance: {account.balance}, Initial staked: {staked}")
        logger.debug(f"Unstake - Amount: {amount}, Gas cost: {gas_cost}")

        # Create and confirm transaction
        tx = MockTransaction(
            from_address=address,  # User initiates the unstake
            to_address=self.address,  # To contract
            value=Decimal("0"),  # No value transfer needed since contract handles balance internally
            gas_limit=self.gas_limit,
            gas_price=self.blockchain.gas_price,
            nonce=self._get_next_nonce(address)
        )
        tx.confirm()
        self.blockchain.apply_transaction(tx)

        # Update stakes after transaction is successful
        self.stakes[address] -= amount  # Update the staked amount
        if self.stakes[address] == 0:
            del self.stakes[address]  # Remove stake entry if fully unstaked

        # Add unstaked amount back to user's balance
        account.balance += amount

        logger.debug(f"Unstake - Final stakes: {self.stakes}")
        return tx

    def get_stake(self, address: str) -> Decimal:
        """Get stake amount for an address."""
        return self.stakes.get(address, Decimal("0"))

    def get_rewards(self, address: str) -> Decimal:
        """Get unclaimed rewards for an address."""
        base_rewards = self.rewards.get(address, Decimal("0"))
        
        # If not staking, just return existing rewards
        if address not in self.stakes:
            return base_rewards
            
        # Calculate additional rewards based on blocks passed
        stake = self.stakes[address]
        stake_block = self.stake_block.get(address, self.blockchain.current_block)
        blocks_passed = self.blockchain.current_block - stake_block
        
        # Calculate rewards: (stake * APR * blocks_passed) / blocks_per_year
        # Assuming 1 block every ~12 seconds = ~2,628,000 blocks per year
        blocks_per_year = Decimal("2628000")
        additional_rewards = (stake * self.apr * blocks_passed) / blocks_per_year
        
        return base_rewards + additional_rewards

    def get_apr(self) -> Decimal:
        """Get current Annual Percentage Rate (APR).

        Returns:
            Current APR as a decimal
        """
        return self.apr

    def get_previous_apr(self) -> Decimal:
        """Get previous Annual Percentage Rate (APR).

        Returns:
            Previous APR as a decimal
        """
        return self._previous_apr

    def add_rewards(self, address: str, amount: Decimal) -> None:
        """Add rewards for a given address."""
        if address not in self.rewards:
            self.rewards[address] = Decimal("0")
        self.rewards[address] += amount

    def claim_rewards(self, address: str) -> MockTransaction:
        """Claim staking rewards.

        Args:
            address: Address claiming rewards

        Returns:
            Transaction details
        """
        # Get current rewards
        rewards = self.get_rewards(address)
        if rewards == 0:
            raise ValueError("No rewards available to claim")

        gas_cost = self._calculate_gas_cost()
        account = self.blockchain.get_account(address)

        # Create and confirm transaction
        tx = MockTransaction(
            from_address=self.address,
            to_address=address,
            value=rewards,
            gas_limit=self.gas_limit,
            gas_price=self.blockchain.gas_price,
            nonce=self._get_next_nonce(address)
        )
        tx.confirm()

        # Transfer rewards to staker
        contract_account = self.blockchain.get_account(self.address)
        contract_account.balance -= rewards
        account.balance += rewards

        # Reset rewards to 0
        self.rewards[address] = Decimal("0")

        return tx

    def get_staked_amount(self, address: str) -> Decimal:
        """Get staked amount for an address.

        Args:
            address: Staker's Ethereum address

        Returns:
            Amount of ETH staked
        """
        return self.stakes.get(address, Decimal("0"))

    def stake_tokens(self, address: str, amount: Decimal) -> None:
        """Stake tokens for address."""
        if address not in self.stakes:
            self.stakes[address] = amount
        else:
            self.stakes[address] += amount

    def compound_rewards(self, address: str) -> None:
        """Compound rewards for address."""
        rewards = self.get_rewards(address)
        if rewards > 0:
            self.stakes[address] += rewards
            account = self.blockchain.get_account(address)
            account.rewards = Decimal("0")

    def compound(self, address: str) -> MockTransaction:
        """Compound rewards for an address.
            
            Args:
                address: The address to compound rewards for
                
            Returns:
                Transaction details
                
            Raises:
                ValueError: If no stake or rewards found for address
            """
        if address not in self.stakes:
            raise ValueError("No stake found")
            
        rewards = self.get_rewards(address)
        if rewards <= 0:
            raise ValueError("No rewards to compound")
            
        # Calculate gas cost
        gas_cost = self._calculate_gas_cost()
        account = self.blockchain.get_account(address)
        logger.debug(f"Compound - Initial balance: {account.balance}, Initial staked: {account.staked_amount}")
        logger.debug(f"Compound - Initial stakes: {self.stakes}")
        logger.debug(f"Compound - Rewards: {rewards}, Gas cost: {gas_cost}")
        
        # Create transaction
        tx = MockTransaction(
            from_address=address,
            to_address=self.address,
            value=rewards,
            gas_limit=self.gas_limit,
            gas_price=self.blockchain.gas_price,
            nonce=self._get_next_nonce(address)
        )
        
        # Update state
        self.stakes[address] = self.stakes[address] + rewards
        self.rewards[address] = Decimal("0")
        account.last_stake_time = self.blockchain.last_block_time
        
        logger.debug(f"Compound - Final stakes: {self.stakes}")
        
        # Confirm transaction
        tx.confirm()
        
        return tx

    def set_apr(self, apr: Decimal) -> None:
        """Set the APR for staking.

        Args:
            apr: APR as a decimal (e.g. 0.05 for 5%)
        """
        self._previous_apr = self.apr
        self.apr = apr

    def _calculate_gas_cost(self) -> Decimal:
        """Calculate gas cost for a transaction.

        Returns:
            Gas cost in ETH
        """
        return (Decimal(self.GAS_LIMIT) * self.blockchain.gas_price) / Decimal("1000000000000000000")  # Convert wei to ETH
