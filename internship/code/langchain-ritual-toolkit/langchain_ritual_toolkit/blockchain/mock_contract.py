"""Mock staking contract implementation."""

from decimal import Decimal
from typing import Dict, Optional, Any

from .mock_state import MockBlockchainState

class MockStakingContract:
    """Mock staking contract for testing."""
    
    def __init__(self, blockchain: MockBlockchainState):
        """Initialize mock staking contract."""
        self.blockchain = blockchain
        
    def stake(self, address: str, amount: Decimal, validator: Optional[str] = None) -> Dict[str, Any]:
        """Stake tokens."""
        current_balance = self.blockchain.get_balance(address)
        if current_balance < amount:
            raise ValueError(f"Insufficient balance: {current_balance} < {amount}")
            
        self.blockchain.set_balance(address, current_balance - amount)
        current_stake = self.blockchain.get_stake(address, validator)
        self.blockchain.set_stake(address, current_stake + amount, validator)
        
        return {
            "success": True,
            "txHash": "0xmock",
            "amount": str(amount),
            "validator": validator or "default"
        }
