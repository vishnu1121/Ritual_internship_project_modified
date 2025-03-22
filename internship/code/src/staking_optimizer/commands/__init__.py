"""Command parsing and intent recognition for the StakingOptimizer.

This package provides functionality for parsing natural language commands
and recognizing user intents.
"""

from .parser import CommandParser
from .models import Intent, IntentClassification
from .templates import ResponseTemplates

__all__ = ["CommandParser", "Intent", "IntentClassification", "ResponseTemplates"]
