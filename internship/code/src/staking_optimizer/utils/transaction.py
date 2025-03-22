"""Transaction formatting utilities.

This module provides utilities for formatting blockchain transaction data
in a consistent way across the application.
"""

from decimal import Decimal
from typing import Any, Dict, Union

from ..blockchain import MockTransaction


def format_transaction(tx: Union[MockTransaction, Dict[str, Any]]) -> Dict[str, str]:
    """Format a transaction for display.

    This function handles both MockTransaction objects and dictionary inputs,
    providing consistent formatting for transaction details including ETH values,
    gas prices, and transaction status.

    Args:
        tx: Transaction to format, can be either a MockTransaction object
            or a dictionary containing transaction details

    Returns:
        Dictionary with formatted transaction details containing:
            - hash: Transaction hash
            - from: Sender address
            - to: Recipient address
            - value: Amount in ETH (6 decimal places)
            - gas_used: Gas used by the transaction
            - gas_price: Gas price in gwei (2 decimal places)
            - status: Transaction status (pending/success/failed)

    Examples:
        >>> tx = MockTransaction(...)
        >>> format_transaction(tx)
        {
            'hash': '0x123...',
            'from': '0xabc...',
            'to': '0xdef...',
            'value': '1.234567 ETH',
            'gas_used': '21000',
            'gas_price': '50.00 gwei',
            'status': 'success'
        }
    """
    # Status mapping for consistent status representation
    status_map = {
        "pending": "pending",
        "success": "success",
        "confirmed": "success",  # Map confirmed to success
        "failed": "failed",
        "reverted": "failed"
    }

    # Handle dictionary input
    if isinstance(tx, dict):
        # Extract and convert ETH value
        value = tx.get('value', '0')
        if isinstance(value, str) and 'ETH' in value:
            value = float(value.replace(' ETH', ''))
        
        # Extract and convert gas price
        gas_price = tx.get('gas_price', '0')
        if isinstance(gas_price, str) and 'gwei' in gas_price:
            gas_price = float(gas_price.replace(' gwei', ''))

        # Map status
        status = tx.get("status", "pending")
        status = "success" if status == "confirmed" else status

        return {
            "hash": tx["hash"],
            "from": tx["from"],
            "to": tx.get("to", ""),
            "value": f"{float(value):.6f} ETH",
            "gas_used": str(tx.get("gas_used", 0)),
            "gas_price": f"{float(gas_price):.2f} gwei",
            "status": status_map.get(status, status)
        }
    
    # Handle MockTransaction input
    return {
        "hash": tx.hash,
        "from": tx.from_address,
        "to": tx.to_address,
        "value": f"{float(tx.value):.6f} ETH",
        "gas_used": str(tx.gas_used),
        "gas_price": f"{float(tx.gas_price / Decimal('1000000000')):.2f} gwei",  # Convert wei to gwei
        "status": status_map.get(tx.status, tx.status)
    }
