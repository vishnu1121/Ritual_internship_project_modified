"""Mock blockchain state implementation."""

from decimal import Decimal
from typing import Dict, Optional

class MockBlockchainState:
    """Mock blockchain state for testing."""
    
    def __init__(self):
        """Initialize mock blockchain state."""
        self.balances: Dict[str, Decimal] = {}
        self.stakes: Dict[str, Dict[str, Decimal]] = {}
        
    def get_balance(self, address: str) -> Decimal:
        """Get balance for an address."""
        return self.balances.get(address, Decimal('0'))
        
    def set_balance(self, address: str, amount: Decimal):
        """Set balance for an address."""
        self.balances[address] = amount
        
    def get_stake(self, address: str, validator: Optional[str] = None) -> Decimal:
        """Get stake amount for an address."""
        if address not in self.stakes:
            return Decimal('0')
        if validator:
            return self.stakes[address].get(validator, Decimal('0'))
        return sum(self.stakes[address].values())
        
    def set_stake(self, address: str, amount: Decimal, validator: Optional[str] = None):
        """Set stake amount for an address."""
        if address not in self.stakes:
            self.stakes[address] = {}
        if validator:
            self.stakes[address][validator] = amount
        else:
            # Use default validator
            self.stakes[address]['default'] = amount
