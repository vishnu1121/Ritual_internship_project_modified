"""Mock blockchain transaction implementation.

This module provides a mock implementation of Ethereum-like blockchain transactions,
simulating core transaction functionality including:
    - Transaction creation and validation
    - State transitions (pending -> confirmed/failed)
    - Gas cost calculations
    - Nonce tracking
    - Error handling

The implementation prioritizes simplicity and testability while maintaining realistic
blockchain behavior. It is designed to work with MockBlockchainState and MockStakingContract
for end-to-end testing of staking operations.

Key Features:
    - Unique transaction hashes
    - Gas cost simulation
    - Transaction status tracking
    - Error message handling
    - Timestamp-based ordering

Typical usage example:
    tx = MockTransaction(
        from_address="0x123",
        to_address="0x456",
        value=Decimal("1.0"),
        nonce=0,
        gas_price=Decimal("20000000000")
    )
    tx.confirm()  # Mark as successful
    gas_cost = tx.get_gas_cost()
"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import uuid4


@dataclass
class MockTransaction:
    """Represents a blockchain transaction with state tracking.

    This class simulates an Ethereum-like transaction with support for
    basic operations like confirmation and gas calculations. It follows
    these key principles:
    1. Immutable after creation - state changes only affect status and gas
    2. Fail-fast validation - invalid parameters raise immediate errors
    3. Realistic behavior - follows Ethereum transaction mechanics
    4. Deterministic - operations have predictable outcomes

    Attributes:
        from_address: Sender's Ethereum address (0x + 40 hex chars)
        to_address: Recipient's Ethereum address (0x + 40 hex chars)
        value: Transaction amount in ETH (must be non-negative)
        nonce: Transaction sequence number (must be non-negative)
        gas_price: Price per gas unit in wei (must be positive)
        gas_limit: Maximum gas units allowed (must be positive)
        gas_used: Actual gas used after confirmation (None if pending)
        hash: Unique transaction identifier (0x + 64 hex chars)
        status: Current transaction state ('pending', 'confirmed', 'failed')
        timestamp: When transaction was created (UTC)
        error: Error message if transaction failed (None if successful)

    Raises:
        ValueError: If any parameters violate the invariants
    """
    from_address: str
    to_address: str
    value: Decimal
    nonce: int
    gas_price: Decimal
    gas_limit: int = 21000  # Default gas limit for ETH transfers
    gas_used: Optional[int] = None  # Actual gas used, set after confirmation
    hash: str = None
    status: str = "pending"
    timestamp: datetime = None
    error: Optional[str] = None

    def __post_init__(self):
        """Initialize transaction with defaults and validations.
        
        This method is called after dataclass initialization to:
            1. Generate a unique transaction hash if not provided
            2. Set creation timestamp if not provided
            3. Convert numeric values to Decimal type
            4. Validate all transaction parameters

        Raises:
            ValueError: If any parameters violate transaction constraints:
                - Negative value or nonce
                - Non-positive gas price or limit
        """
        # Generate random hash if not provided
        if not self.hash:
            # Generate a 32-byte (64 hex chars) hash
            tx_hash = uuid4().hex + uuid4().hex[:32]
            self.hash = f"0x{tx_hash}"
        
        # Set timestamp if not provided
        if not self.timestamp:
            self.timestamp = datetime.now()

        # Basic validations
        if not isinstance(self.value, Decimal):
            self.value = Decimal(str(self.value))
        if not isinstance(self.gas_price, Decimal):
            self.gas_price = Decimal(str(self.gas_price))
        if self.value < 0:
            raise ValueError("Transaction value cannot be negative")
        if self.nonce < 0:
            raise ValueError("Transaction nonce cannot be negative")
        if self.gas_price <= 0:
            raise ValueError("Gas price must be positive")
        if self.gas_limit <= 0:
            raise ValueError("Gas limit must be positive")

    def confirm(self, success: bool = True, error: str = None) -> None:
        """Mark transaction as confirmed or failed.
        
        Updates transaction status and gas usage based on confirmation result.
        For successful transactions, sets gas_used to 95% of limit to simulate
        realistic gas consumption. Failed transactions consume full gas limit.

        Args:
            success: Whether the transaction succeeded
            error: Error message if transaction failed, ignored if success=True

        Note:
            Gas is still consumed even if transaction fails, following Ethereum's
            behavior where failed transactions still pay for computation.
        """
        if success:
            self.status = "success"
            # Set gas used to actual amount on success (use 95% of limit as typical case)
            self.gas_used = int(self.gas_limit * 0.95)  # More realistic gas usage
        else:
            self.status = "failed"
            self.error = error
            # Failed transactions still consume full gas
            self.gas_used = self.gas_limit

    def get_gas_cost(self) -> Decimal:
        """Calculate total gas cost in ETH.
        
        Calculates the total cost of gas used by the transaction, converting
        from wei to ETH. For pending transactions, uses gas_limit as worst case.

        Returns:
            Decimal: Total gas cost in ETH (gas_used * gas_price converted to ETH)

        Note:
            Conversion uses 1 ETH = 10^18 wei
        """
        gas = self.gas_used if self.gas_used is not None else self.gas_limit
        return Decimal(str(gas)) * self.gas_price / Decimal("1000000000000000000")  # Convert wei to ETH

    def to_dict(self) -> dict:
        """Convert transaction to dictionary format.
        
        Creates a dictionary representation of the transaction suitable for
        serialization or API responses. All numeric values are converted to
        strings to maintain precision.

        Returns:
            dict: Dictionary containing all transaction fields:
                - hash: Transaction hash (0x-prefixed hex)
                - from: Sender address
                - to: Recipient address
                - value: Transaction amount in ETH (as string)
                - nonce: Transaction sequence number
                - gas_price: Gas price in wei (as string)
                - gas_limit: Maximum gas units
                - gas_used: Actual gas used (or None if pending)
                - status: Transaction status
                - timestamp: Creation time (ISO format)
                - error: Error message if failed (or None)
        """
        return {
            "hash": self.hash,
            "from": self.from_address,
            "to": self.to_address,
            "value": str(self.value),
            "nonce": self.nonce,
            "gas_price": str(self.gas_price),
            "gas_limit": self.gas_limit,
            "gas_used": self.gas_used,
            "status": self.status,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "error": self.error
        }
