"""Mock blockchain state for testing.

This module provides a mock implementation of an Ethereum-like blockchain state for testing
staking operations. It simulates core blockchain functionality including:
    - Account management (creation, balance tracking)
    - Transaction processing (transfers, gas costs)
    - Block mining and rewards
    - Staking operations (stake, unstake, rewards)

The implementation prioritizes simplicity and testability over performance, making it
suitable for unit and integration testing of staking-related functionality.

Typical usage example:
    blockchain = MockBlockchainState(chain_id=1)
    account = blockchain.create_account("0x123", 1.0)
    tx = blockchain.transfer("0x123", "0x456", 0.5)
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, Optional
import uuid
import logging

logger = logging.getLogger(__name__)

@dataclass
class Account:
    """Mock blockchain account.
    
    Represents an account on the mock blockchain, tracking balances,
    staking amounts, and transaction nonces.

    Attributes:
        address: Ethereum-style address (0x-prefixed hex string)
        balance: Account balance in ETH
        staked_amount: Amount of ETH currently staked
        rewards: Unclaimed staking rewards in ETH
        nonce: Number of transactions sent from this account
        last_stake_time: Timestamp of last stake operation
    """

    address: str
    balance: Decimal
    staked_amount: Decimal = Decimal("0")
    rewards: Decimal = Decimal("0")
    nonce: int = 0
    last_stake_time: Optional[datetime] = None


@dataclass
class MockTransaction:
    """Mock blockchain transaction.
    
    Represents a transaction on the mock blockchain, tracking all relevant
    transaction data including gas costs and execution status.

    Attributes:
        from_address: Sender's address
        to_address: Recipient's address
        value: Amount of ETH to transfer
        gas_limit: Maximum gas units allowed
        gas_price: Price per gas unit in wei
        nonce: Sender's transaction count
        hash: Unique transaction identifier (0x-prefixed 64-char hex)
        status: Transaction status ('pending' or 'success')
        timestamp: When transaction was created
        error: Error message if transaction failed
        gas_used: Actual gas used by transaction
    """

    from_address: str
    to_address: str
    value: Decimal
    gas_limit: Decimal
    gas_price: Decimal
    nonce: int
    hash: str = field(default_factory=lambda: f"0x{uuid.uuid4().hex:0>64}")  # Pad with zeros to get 64 hex chars + 0x prefix
    status: str = "pending"
    timestamp: datetime = field(default_factory=datetime.now)
    error: str = None
    gas_used: Decimal = field(default=None)

    def confirm(self):
        """Confirm transaction and set gas used."""
        self.status = "success"
        if self.gas_used is None:
            self.gas_used = self.gas_limit  # Assume gas limit is used for simplicity

    def get_gas_cost(self) -> Decimal:
        """Calculate gas cost in ETH.

        Returns:
            Gas cost in ETH
        """
        if self.gas_used is None:
            self.gas_used = self.gas_limit  # Assume gas limit is used for simplicity
        return (self.gas_used * self.gas_price) / Decimal("1000000000000000000")  # Convert wei to ETH


class MockBlockchainState:
    """Mock blockchain state for testing.

    This class provides a mock implementation of an Ethereum-like blockchain state for testing
    staking operations. It maintains a list of accounts and transactions, and provides methods for
    common blockchain operations like transfers and staking.

    The implementation follows these key design principles:
    1. Simplicity over performance - operations are straightforward and easy to understand
    2. Fail-fast with clear errors - invalid operations raise descriptive exceptions
    3. Realistic behavior - simulates gas costs, nonces, and other blockchain mechanics
    4. Deterministic - operations have predictable outcomes for testing

    Attributes:
        chain_id: Chain ID for the mock blockchain
        accounts: Mapping of address to account details
        transactions: Dictionary of transaction hash to transaction details
        gas_price: Current gas price in wei (default: 20 gwei)
        last_block_time: Timestamp of last mined block
        current_block: Current block number
        _block_number: Internal block number counter
        _staking_apr: Annual percentage rate for staking rewards
        gas_limit: Standard gas limit for basic transactions

    Raises:
        KeyError: If attempting to access a nonexistent account
        ValueError: If attempting an invalid operation (e.g. insufficient funds)
    """

    def __init__(self, chain_id: int = 1) -> None:
        """Initialize mock blockchain state.

        Args:
            chain_id: Chain ID for the mock blockchain
        """
        self.chain_id = chain_id
        self.accounts: Dict[str, Account] = {}
        self.transactions: Dict[str, MockTransaction] = {}
        self.gas_price = Decimal("20000000000")  # 20 gwei
        self.last_block_time = datetime.now()
        self.current_block = 0  # Start at block 0
        self._block_number = 0
        self._staking_apr = Decimal("10.0")  # 10% APR
        self.gas_limit = Decimal("21000")  # Standard gas limit for basic transactions

    def create_account(self, address: str, balance: float = 0.0) -> Account:
        """Create a new account with initial balance.

        Args:
            address: Account address
            balance: Initial balance in ETH

        Returns:
            Created account

        Raises:
            ValueError: If account already exists
        """
        logger.debug(f"Creating new account for {address} with balance: {balance}")
        if address in self.accounts:
            raise ValueError(f"Account {address} already exists")

        account = Account(
            address=address,
            balance=Decimal(str(balance)),
            staked_amount=Decimal("0")
        )
        self.accounts[address] = account
        logger.debug(f"Account state after creation - Address: {address}, Balance: {self.get_balance(address)}")
        return account

    def get_account(self, address: str) -> Account:
        """Get account details.

        Args:
            address: Account address

        Returns:
            Account details

        Raises:
            KeyError: If account does not exist
        """
        if address not in self.accounts:
            raise KeyError(f"Account {address} does not exist")
        return self.accounts[address]

    def get_balance(self, address: str) -> Decimal:
        """Get account balance.

        Args:
            address: Account address

        Returns:
            Account balance in ETH

        Raises:
            KeyError: If account does not exist
        """
        balance = self.accounts[address].balance
        logger.debug(f"Getting balance for {address}: {balance}")
        return balance

    def get_staking_apr(self) -> Decimal:
        """Get current staking APR.

        Returns:
            APR as a decimal (e.g. 0.05 for 5%)
        """
        return self._staking_apr

    def get_gas_price(self) -> Decimal:
        """Get current gas price in gwei.

        Returns:
            Gas price in gwei
        """
        return self.gas_price / Decimal("1000000000")
    
    def set_gas_price(self, price: Decimal) -> None:
        """Set gas price.

        Args:
            price: New gas price in gwei
        """
        self.gas_price = price * Decimal("1000000000")

    def get_staked_amount(self, address: str) -> str:
        """Get staked amount for address.

        Args:
            address: Account address

        Returns:
            Staked amount in ETH as string
        """
        account = self.get_account(address)
        return str(account.staked_amount)

    def get_block_number(self) -> int:
        """Get current block number.

        Returns:
            Current block number
        """
        return self._block_number

    def mine_block(self) -> None:
        """Mine a new block.

        This updates block number, last block time, and processes staking rewards.
        """
        self._block_number += 1
        self.current_block += 1
        self.last_block_time += timedelta(seconds=12)  # ~12 second blocks
        
        # Calculate and distribute staking rewards
        for account in self.accounts.values():
            if account.staked_amount > 0 and account.last_stake_time:
                time_staked = self.last_block_time - account.last_stake_time
                reward_rate = self._staking_apr / Decimal("365") / Decimal("86400")
                reward = account.staked_amount * reward_rate * Decimal(str(time_staked.total_seconds()))
                account.rewards += reward
                
        # Update last block time to current time
        self.last_block_time = datetime.now()

    def transfer(self, from_address: str, to_address: str, amount: Decimal) -> MockTransaction:
        """Transfer ETH between accounts.

        Args:
            from_address: Sender address
            to_address: Recipient address
            amount: Amount to transfer in ETH

        Returns:
            Transaction details

        Raises:
            KeyError: If sender account does not exist
            ValueError: If insufficient balance
        """
        # Get sender account (will raise KeyError if not found)
        from_account = self.get_account(from_address)

        # Create recipient account if it doesn't exist
        if to_address not in self.accounts:
            self.create_account(to_address)

        # Create transaction
        tx = MockTransaction(
            from_address=from_address,
            to_address=to_address,
            value=amount,
            gas_limit=self.gas_limit,
            gas_price=self.gas_price,
            nonce=from_account.nonce
        )

        # Check if sender has sufficient balance (value + gas)
        total_cost = amount + tx.get_gas_cost()
        if from_account.balance < total_cost:
            raise ValueError(f"Insufficient balance. Required: {total_cost} ETH, Available: {from_account.balance} ETH")

        # Apply transaction
        self.apply_transaction(tx)
        from_account.nonce += 1

        return tx

    def apply_transaction(self, tx: MockTransaction) -> None:
        """Apply a transaction to the blockchain state.

        Args:
            tx: Transaction to apply
        """
        # Calculate gas cost
        gas_cost = tx.get_gas_cost()
        logger.debug(f"Processing transaction: {tx}")
        logger.debug(f"Gas cost for transaction: {gas_cost} ETH")

        # Log initial state
        logger.debug(f"BEFORE TX - From address ({tx.from_address}) balance: {self.get_balance(tx.from_address)}")
        logger.debug(f"BEFORE TX - To address ({tx.to_address}) balance: {self.get_balance(tx.to_address)}")

        # Calculate total cost (value + gas)
        total_cost = tx.value + gas_cost
        logger.debug(f"Total cost (value + gas): {total_cost} ETH")

        # Update sender balance (deduct value + gas)
        sender_old_balance = self.get_balance(tx.from_address)
        self.accounts[tx.from_address].balance -= total_cost
        logger.debug(f"Updated sender balance: {sender_old_balance} -> {self.get_balance(tx.from_address)}")

        # Update recipient balance (add value only)
        recipient_old_balance = self.get_balance(tx.to_address)
        self.accounts[tx.to_address].balance += tx.value  # Don't deduct gas from recipient
        logger.debug(f"Updated recipient balance: {recipient_old_balance} -> {self.get_balance(tx.to_address)}")

        # Store transaction
        self.transactions[tx.hash] = tx

        # Log final state
        logger.debug(f"AFTER TX - From address ({tx.from_address}) balance: {self.get_balance(tx.from_address)}")
        logger.debug(f"AFTER TX - To address ({tx.to_address}) balance: {self.get_balance(tx.to_address)}")

    def stake(self, address: str, amount: str) -> str:
        """Stake ETH.

        Args:
            address: Account address
            amount: Amount to stake in ETH

        Returns:
            Transaction hash

        Raises:
            ValueError: If amount is invalid or account has insufficient balance
        """
        account = self.get_account(address)
        amount = Decimal(amount)
        gas_cost = (Decimal("100000") * self.gas_price) / Decimal("1000000000000000000")  # Convert wei to ETH
        total_cost = amount + gas_cost
        logger.debug(f"Stake - Initial balance: {account.balance}, Initial staked: {account.staked_amount}")
        logger.debug(f"Stake - Amount: {amount}, Gas cost: {gas_cost}")

        if amount <= 0:
            raise ValueError("Amount must be positive")
        if total_cost > account.balance:
            raise ValueError("Insufficient balance including gas costs")

        # Create and apply transaction first
        tx = MockTransaction(
            from_address=address,  # User initiates the stake
            to_address="0x0000000000000000000000000000000000000000",  # To contract
            value=amount,  # Send the staked amount
            gas_limit=Decimal("100000"),
            gas_price=self.gas_price,
            nonce=account.nonce
        )
        tx.confirm()  # Set gas_used
        self.apply_transaction(tx)
        account.nonce += 1

        # Update staking state after transaction is processed
        account.staked_amount += amount
        account.last_stake_time = self.last_block_time
        logger.debug(f"Stake - Final balance: {account.balance}, Final staked: {account.staked_amount}")

        return tx.hash

    def unstake(self, address: str, amount: str) -> str:
        """Unstake ETH.

        Args:
            address: Account address
            amount: Amount to unstake in ETH

        Returns:
            Transaction hash

        Raises:
            ValueError: If amount is invalid or account has insufficient staked balance
        """
        account = self.get_account(address)
        amount = Decimal(amount)
        gas_cost = (Decimal("100000") * self.gas_price) / Decimal("1000000000000000000")  # Convert wei to ETH
        logger.debug(f"Unstake - Initial balance: {account.balance}, Initial staked: {account.staked_amount}")
        logger.debug(f"Unstake - Amount: {amount}, Gas cost: {gas_cost}")

        if amount <= 0:
            raise ValueError("Amount must be positive")
        if amount > account.staked_amount:
            raise ValueError("Insufficient staked balance")
        if gas_cost > account.balance:
            raise ValueError("Insufficient balance for gas costs")

        # Create and apply transaction first
        tx = MockTransaction(
            from_address=address,  # User initiates the unstake
            to_address="0x0000000000000000000000000000000000000000",  # To contract
            value=Decimal("0"),  # No value transfer needed since contract handles balance internally
            gas_limit=Decimal("100000"),
            gas_price=self.gas_price,
            nonce=account.nonce
        )
        tx.confirm()  # Set gas_used
        self.apply_transaction(tx)
        account.nonce += 1

        # Update staking state after transaction is processed
        account.staked_amount -= amount
        account.balance += amount  # Add unstaked amount back to balance
        logger.debug(f"Unstake - Final balance: {account.balance}, Final staked: {account.staked_amount}")

        return tx.hash

    def claim_rewards(self, address: str) -> str:
        """Claim staking rewards.

        Args:
            address: Account address

        Returns:
            Transaction hash

        Raises:
            ValueError: If no rewards to claim
        """
        account = self.get_account(address)

        if account.rewards <= 0:
            raise ValueError("No rewards to claim")

        rewards = account.rewards
        account.balance += rewards
        account.rewards = Decimal("0")

        tx = MockTransaction(
            from_address="0x0000000000000000000000000000000000000000",
            to_address=address,
            value=rewards,
            gas_limit=Decimal("21000"),
            gas_price=self.gas_price,
            nonce=account.nonce
        )
        self.transactions[tx.hash] = tx
        account.nonce += 1

        return tx.hash

    def get_rewards(self, address: str) -> str:
        """Get unclaimed rewards for address.

        Args:
            address: Account address

        Returns:
            Unclaimed rewards in ETH as string
        """
        account = self.get_account(address)
        return str(account.rewards)

    def set_balance(self, address: str, balance: Decimal) -> None:
        """Set account balance.

        Args:
            address: Account address
            balance: New balance in ETH

        Raises:
            KeyError: If account does not exist
        """
        old_balance = self.get_balance(address)
        logger.debug(f"Setting balance for {address} from {old_balance} to {balance}")
        self.accounts[address].balance = balance
        logger.debug(f"Account state after setting balance - Address: {address}, Balance: {self.get_balance(address)}")
