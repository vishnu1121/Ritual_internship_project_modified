"""Command models for the StakingOptimizer.

This module defines the data models for various staking commands.
Each command type has its own model with specific validation rules.
"""

from enum import Enum
from typing import Optional, Union, Dict, Literal
from decimal import Decimal
from pydantic import BaseModel, Field, field_validator

class CommandType(str, Enum):
    """Type of staking command."""
    STAKE = "stake"
    UNSTAKE = "unstake"
    COMPOUND = "compound"
    VIEW = "view"
    INFO = "info"  # New type for informational queries

class Intent(str, Enum):
    """User intent for the command."""
    STAKE = "stake"
    UNSTAKE = "unstake"
    COMPOUND = "compound"
    VIEW = "view"
    INFO = "info"
    CLAIM = "claim"
    HELP = "help"
    UNKNOWN = "unknown"

class IntentClassification(BaseModel):
    """Intent classification output.
    
    This model is used to classify user intents before converting them
    to strongly-typed commands. It provides a way to capture the user's
    intent along with any extracted parameters and confidence scores.
    
    Attributes:
        intent: The classified intent
        parameters: Extracted parameters from the request
        confidence: Confidence score of the classification
    """
    intent: Intent = Field(description="The classified intent of the request")
    parameters: Dict[str, str] = Field(
        default_factory=dict,
        description="Extracted parameters from the request"
    )
    confidence: float = Field(
        default=0.0,
        description="Confidence score of the classification",
        ge=0.0,
        le=1.0
    )

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "intent": "stake",
                    "parameters": {"amount": "100", "token": "ETH"},
                    "confidence": 0.9
                }
            ]
        }

class StakingCommand:
    """Base class for staking commands."""
    pass

class StakeCommand(BaseModel):
    """Command to stake ETH."""
    address: str = Field(description="Ethereum address to stake from")
    amount: float = Field(description="Amount of ETH to stake", gt=0)
    validator: Optional[str] = Field(None, description="Optional validator address to stake with")

class UnstakeCommand(StakingCommand):
    """Command to unstake ETH.
    
    Attributes:
        address: Ethereum address to unstake from
        amount: Amount to unstake in ETH, or 'all' to unstake entire balance
        unstake_all: True if unstaking entire balance
    """
    def __init__(self, address: str, amount: Union[float, str]):
        self.address = address
        # Handle unstake all case
        if isinstance(amount, str) and amount.lower() == 'all':
            self.unstake_all = True
            self.amount = 'all'  # Keep 'all' as string instead of None
        else:
            self.unstake_all = False
            # Convert to Decimal for precision
            try:
                self.amount = Decimal(str(amount))
                if self.amount <= 0:
                    raise ValueError("Amount to unstake must be greater than 0")
            except (TypeError, ValueError) as e:
                raise ValueError(f"Invalid unstake amount: {str(e)}")

class CompoundCommand(StakingCommand):
    """Command to compound rewards."""
    def __init__(self, address: str):
        self.address = address
        self.action = "compound"

class ViewCommand(StakingCommand):
    """Command to view staking information."""
    def __init__(self, address: str, view_type: str):
        self.address = address
        self.view_type = view_type
        self.original_request = None  # Will be set by the parser

class InformationalCommand(StakingCommand):
    """Command to get information about staking."""
    def __init__(self, topic: str):
        self.topic = topic

# Union type for all possible commands
StakingCommand = Union[
    StakeCommand,
    UnstakeCommand,
    CompoundCommand,
    ViewCommand,
    InformationalCommand
]
