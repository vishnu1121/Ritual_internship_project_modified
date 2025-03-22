"""Mock blockchain and contract implementations for testing."""
from dataclasses import dataclass
from decimal import Decimal
from typing import Dict, Optional
import logging


@dataclass
class MockAccount:
    """Mock account for testing."""
    address: str
    balance: Decimal


@dataclass
class MockTransaction:
    """Mock transaction for testing."""
    hash: str
    from_address: str
    to_address: str
    value: Decimal
    gas_used: int
    gas_price: Decimal
    status: str
    confirmed: bool = True


class MockBlockchainState:
    """Mock blockchain state for testing."""

    def __init__(self):
        """Initialize mock blockchain state."""
        self.accounts: Dict[str, MockAccount] = {}
        self.gas_price = Decimal("1000000000")  # 1 gwei
        self.block_number = 1000000

    def get_account(self, address: str) -> MockAccount:
        """Get account by address."""
        if address not in self.accounts:
            self.accounts[address] = MockAccount(
                address=address,
                balance=Decimal("10.0")
            )
        return self.accounts[address]

    def get_block_number(self) -> int:
        """Get current block number."""
        return self.block_number

    def get_balance(self, address: str) -> Decimal:
        """Get balance for address."""
        return self.get_account(address).balance

    def update_balance(self, address: str, amount: Decimal):
        """Update balance for address."""
        account = self.get_account(address)
        account.balance = amount

    def apply_transaction(self, tx: MockTransaction):
        """Apply transaction effects to blockchain state.
        
        This includes:
        1. Transferring value from sender to recipient
        2. Deducting gas costs from sender
        
        Args:
            tx: Transaction to apply
        """
        logger = logging.getLogger(__name__)
        
        # Get accounts
        from_account = self.get_account(tx.from_address)
        to_account = self.get_account(tx.to_address)
        
        # Calculate gas cost
        gas_cost = Decimal(str(tx.gas_used)) * tx.gas_price
        
        # Log transaction details
        logger.debug(f"Applying transaction:")
        logger.debug(f"From: {tx.from_address} (balance: {from_account.balance})")
        logger.debug(f"To: {tx.to_address} (balance: {to_account.balance})")
        logger.debug(f"Value: {tx.value}")
        logger.debug(f"Gas cost: {gas_cost}")
        
        # Update balances
        from_account.balance -= (tx.value + gas_cost)
        to_account.balance += tx.value
        
        logger.debug(f"New balances:")
        logger.debug(f"From: {tx.from_address} (balance: {from_account.balance})")
        logger.debug(f"To: {tx.to_address} (balance: {to_account.balance})")


class MockStakingContract:
    """Mock staking contract for testing."""

    def __init__(self, blockchain: Optional[MockBlockchainState] = None):
        """Initialize mock staking contract.
        
        Args:
            blockchain: Optional blockchain state for gas calculations
        """
        self.blockchain = blockchain
        self._staked: Dict[str, Decimal] = {}
        self._rewards: Dict[str, Decimal] = {}
        self.GAS_LIMIT = 100000

    @property
    def staked(self) -> Dict[str, Decimal]:
        """Get staked amounts."""
        return self._staked

    @property
    def rewards(self) -> Dict[str, Decimal]:
        """Get reward amounts."""
        return self._rewards

    def get_staked_amount(self, address: str) -> Decimal:
        """Get staked amount for address."""
        return self._staked.get(address, Decimal("0"))

    def get_rewards(self, address: str) -> Decimal:
        """Get unclaimed rewards for address."""
        return self._rewards.get(address, Decimal("0"))

    def get_apr(self) -> str:
        """Get current APR."""
        return "5.0%"

    def stake(self, address: str, amount: Decimal) -> MockTransaction:
        """Stake tokens."""
        self._staked[address] = self._staked.get(address, Decimal("0")) + amount
        return MockTransaction(
            hash="0x123",
            from_address=address,
            to_address="contract",
            value=amount,
            gas_used=100000,
            gas_price=Decimal("20000000000"),  # 20 gwei
            status="success"
        )

    def unstake(self, address: str, amount: Decimal) -> MockTransaction:
        """Unstake tokens."""
        if amount > self._staked.get(address, Decimal("0")):
            raise ValueError("Insufficient staked balance")
        self._staked[address] -= amount
        return MockTransaction(
            hash="0x123",
            from_address="contract",
            to_address=address,
            value=amount,
            gas_used=100000,
            gas_price=Decimal("20000000000"),  # 20 gwei
            status="success"
        )

    def claim_rewards(self, address: str) -> MockTransaction:
        """Claim rewards."""
        amount = self._rewards.get(address, Decimal("0"))
        if amount == 0:
            raise ValueError("No rewards to claim")
        self._rewards[address] = Decimal("0")
        return MockTransaction(
            hash="0x123",
            from_address="contract",
            to_address=address,
            value=amount,
            gas_used=100000,
            gas_price=Decimal("1000000000"),
            status="success"
        )

    def compound(self, address: str) -> MockTransaction:
        """Compound rewards."""
        logger = logging.getLogger(__name__)
        
        logger.debug(f"Starting compound for address {address}")
        logger.debug(f"Current staked amount: {self._staked.get(address, Decimal('0'))}")
        logger.debug(f"Current rewards: {self._rewards.get(address, Decimal('0'))}")
        
        rewards = self._rewards.get(address, Decimal("0"))
        if rewards == 0:
            logger.error(f"No rewards to compound for address {address}")
            raise ValueError("No rewards to compound")
            
        self._rewards[address] = Decimal("0")
        current_stake = self._staked.get(address, Decimal("0"))
        new_stake = current_stake + rewards
        self._staked[address] = new_stake
        
        logger.debug(f"After compound - New staked amount: {new_stake}")
        logger.debug(f"After compound - Remaining rewards: {self._rewards[address]}")
        
        return MockTransaction(
            hash="0x123",
            from_address=address,
            to_address="contract",
            value=rewards,
            gas_used=100000,
            gas_price=Decimal("1000000000"),
            status="success"
        )

    def get_compound_history(self, address: str) -> Dict[str, str]:
        """Get compound history for address."""
        return {
            "last_compound": "2024-01-01 00:00:00",
            "total_compounds": "5",
            "total_compounded": "1.5 ETH"
        }
