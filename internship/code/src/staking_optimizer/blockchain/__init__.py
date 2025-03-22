"""Mock blockchain implementation for StakingOptimizer.

This package provides mock implementations of blockchain components for testing
and development purposes. It includes:

- MockBlockchainState: Simulates blockchain state and transactions
- MockTransaction: Represents a blockchain transaction
- MockStakingContract: Simulates a staking contract interface
"""

from .mock_state import MockBlockchainState
from .mock_transaction import MockTransaction
from .mock_contract import MockStakingContract

__all__ = ["MockBlockchainState", "MockTransaction", "MockStakingContract"]
