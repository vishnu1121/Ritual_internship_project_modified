"""Utility module for handling blockchain unit conversions."""

from decimal import Decimal
from typing import Union

# Constants for unit conversions
WEI_PER_GWEI = Decimal("1000000000")  # 10^9
WEI_PER_ETH = Decimal("1000000000000000000")  # 10^18

def wei_to_gwei(wei_amount: Union[Decimal, int, str]) -> Decimal:
    """Convert wei to gwei.
    
    Args:
        wei_amount: Amount in wei
        
    Returns:
        Decimal: Amount in gwei
    """
    return Decimal(str(wei_amount)) / WEI_PER_GWEI

def gwei_to_wei(gwei_amount: Union[Decimal, int, str]) -> Decimal:
    """Convert gwei to wei.
    
    Args:
        gwei_amount: Amount in gwei
        
    Returns:
        Decimal: Amount in wei
    """
    return Decimal(str(gwei_amount)) * WEI_PER_GWEI

def wei_to_eth(wei_amount: Union[Decimal, int, str]) -> Decimal:
    """Convert wei to ETH.
    
    Args:
        wei_amount: Amount in wei
        
    Returns:
        Decimal: Amount in ETH
    """
    return Decimal(str(wei_amount)) / WEI_PER_ETH

def eth_to_wei(eth_amount: Union[Decimal, int, str]) -> Decimal:
    """Convert ETH to wei.
    
    Args:
        eth_amount: Amount in ETH
        
    Returns:
        Decimal: Amount in wei
    """
    return Decimal(str(eth_amount)) * WEI_PER_ETH

def format_gwei(gwei_amount: Union[Decimal, int, str]) -> str:
    """Format gwei amount with unit suffix.
    
    Args:
        gwei_amount: Amount in gwei
        
    Returns:
        str: Formatted string with gwei suffix
    """
    return f"{gwei_amount} gwei"

def format_eth(eth_amount: Union[Decimal, int, str]) -> str:
    """Format ETH amount with unit suffix.
    
    Args:
        eth_amount: Amount in ETH
        
    Returns:
        str: Formatted string with ETH suffix
    """
    return f"{eth_amount} ETH"
