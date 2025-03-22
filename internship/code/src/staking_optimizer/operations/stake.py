"""Stake tokens."""

from decimal import Decimal
from typing import Dict, Optional, Union

from langchain_ritual_toolkit import RitualToolkit

from ..blockchain import MockBlockchainState, MockStakingContract, MockTransaction
from ..utils import format_transaction


def stake_tokens(
    address_or_toolkit: Union[str, RitualToolkit],
    amount_or_address: Union[float, Decimal, str],
    blockchain_or_amount: Union[MockBlockchainState, float, Decimal],
    contract: Optional[MockStakingContract] = None,
    validator: Optional[str] = None,
) -> Dict[str, str]:
    """Stake tokens for an address.

    This function can be called in two ways:
    1. With RitualToolkit:
       stake_tokens(toolkit, address, amount, validator=None)
    2. With MockBlockchain:
       stake_tokens(address, amount, blockchain, contract, validator=None)

    Args:
        address_or_toolkit: Either the address staking tokens or RitualToolkit instance
        amount_or_address: Either amount of tokens to stake or address if first arg is toolkit
        blockchain_or_amount: Either mock blockchain state or amount if first arg is toolkit
        contract: Optional mock staking contract, required if using mock blockchain
        validator: Optional validator address to stake with

    Returns:
        Dictionary with formatted transaction details

    Raises:
        ValueError: If amount is invalid or balance insufficient
        KeyError: If address does not exist
    """
    # Handle toolkit case
    if isinstance(address_or_toolkit, RitualToolkit):
        toolkit = address_or_toolkit
        address = amount_or_address
        amount = blockchain_or_amount
        if not isinstance(address, str):
            raise ValueError("Address must be a string")
        if not isinstance(amount, (float, Decimal)):
            raise ValueError("Amount must be a number")
        tx = toolkit.stake(address, amount, validator)
        return format_transaction(tx)

    # Handle mock blockchain case
    address = address_or_toolkit
    amount = amount_or_address
    blockchain = blockchain_or_amount

    if not isinstance(address, str):
        raise ValueError("Address must be a string")
    if not isinstance(amount, (float, Decimal)):
        raise ValueError("Amount must be a number")
    if not isinstance(blockchain, MockBlockchainState):
        raise ValueError("Expected MockBlockchainState instance")
    if contract is None:
        raise ValueError("Mock staking contract required")

    # Convert amount to Decimal if float
    if isinstance(amount, float):
        amount = Decimal(str(amount))

    # Check balance
    balance = blockchain.get_balance(address)
    if amount > balance:
        raise ValueError(f"Insufficient balance: {balance} ETH")

    # Stake tokens
    tx = contract.stake(address, amount, validator)
    
    return format_transaction(tx)
