"""Safety module for StakingOptimizer.

This package provides safety and validation utilities for the StakingOptimizer agent.
"""
import re
from typing import List


class SafetyValidator:
    """Validator for ensuring user requests are safe."""

    def __init__(self):
        """Initialize the validator."""
        self.blocked_patterns = [
            r"(?i)malicious",
            r"(?i)hack",
            r"(?i)exploit",
            r"(?i)steal",
            r"(?i)attack",
            r"(?i)compromise",
            r"(?i)destroy",
            r"(?i)delete",
        ]

    def is_safe(self, request: str) -> bool:
        """Check if a request is safe.

        Args:
            request: User request to validate

        Returns:
            True if request is safe, False otherwise
        """
        for pattern in self.blocked_patterns:
            if re.search(pattern, request):
                return False
        return True
