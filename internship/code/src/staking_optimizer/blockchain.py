"""Mock blockchain and contract implementations for testing."""
from dataclasses import dataclass
from decimal import Decimal
from typing import Dict, Optional


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
            gas_price=Decimal("1000000000"),
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
            gas_price=Decimal("1000000000"),
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
        rewards = self._rewards.get(address, Decimal("0"))
        if rewards == 0:
            raise ValueError("No rewards to compound")
        self._rewards[address] = Decimal("0")
        self._staked[address] = self._staked.get(address, Decimal("0")) + rewards
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
