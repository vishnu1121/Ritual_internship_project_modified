"""Unstaking operations.

This module provides functionality for unstaking tokens.
"""

from decimal import Decimal
from typing import Dict, Optional

from ..blockchain import MockBlockchainState, MockStakingContract
from ..utils import format_transaction


def unstake_tokens(
    address: str,
    amount: Optional[Decimal],
    blockchain: MockBlockchainState,
    contract: MockStakingContract,
) -> Dict[str, str]:
    """Unstake tokens for an address.

    Args:
        address: The address unstaking tokens
        amount: Amount of tokens to unstake in ETH. If None, unstakes all tokens.
        blockchain: Mock blockchain state
        contract: Mock staking contract

    Returns:
        Dictionary with transaction details

    Raises:
        ValueError: If amount is invalid or staked balance insufficient
        KeyError: If address does not exist
    """
    # Get staking position
    position = contract.get_position(address)
    if position is None:
        raise KeyError(f"No staking position found for {address}")

    # If amount not specified, unstake all
    if amount is None:
        amount = position.staked

    # Check staked balance
    if amount > position.staked:
        raise ValueError(f"Insufficient staked balance: {position.staked} ETH")

    # Unstake tokens
    tx = contract.unstake(address, amount)
    
    # Apply transaction costs
    blockchain.apply_transaction(tx)
    
    return format_transaction(tx)
