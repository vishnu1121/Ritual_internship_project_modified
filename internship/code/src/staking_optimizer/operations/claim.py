"""Operations for claiming staking rewards."""

from decimal import Decimal

from ..blockchain.mock_contract import MockStakingContract
from ..blockchain.mock_state import MockBlockchainState
from ..blockchain.mock_transaction import MockTransaction


def claim_rewards(address: str, blockchain: MockBlockchainState, contract: MockStakingContract) -> MockTransaction:
    """Claim staking rewards.

    Args:
        address: Address claiming rewards
        blockchain: Blockchain state
        contract: Staking contract

    Returns:
        Transaction details
    """
    return contract.claim_rewards(address)
