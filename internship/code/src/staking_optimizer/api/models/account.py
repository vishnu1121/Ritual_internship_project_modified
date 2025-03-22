"""Account models for request/response handling.

This module defines Pydantic models for account-related data.
"""

from datetime import datetime
from pydantic import BaseModel, Field
from decimal import Decimal

class AccountStatus(BaseModel):
    """Account status information.
    
    Attributes:
        address: Ethereum address
        balance: Current ETH balance
        staked: Amount of ETH staked
        rewards: Accumulated rewards
        last_update: Timestamp of last update
    """
    address: str = Field(..., pattern="^0x[a-fA-F0-9]{40}$")
    balance: Decimal
    staked: Decimal
    rewards: Decimal
    last_update: datetime = Field(default_factory=datetime.utcnow)
