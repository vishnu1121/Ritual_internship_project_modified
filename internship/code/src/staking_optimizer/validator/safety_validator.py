"""Safety validator for staking operations."""

import logging
from typing import List, Optional, Set

logger = logging.getLogger(__name__)

class SafetyValidator:
    """Validator for checking safety of staking operations."""

    def __init__(self) -> None:
        """Initialize validator with default patterns."""
        self.blocked_patterns: Set[str] = set()
        self.required_keywords: Set[str] = set()

    def add_blocked_pattern(self, pattern: str) -> None:
        """Add a pattern to block.

        Args:
            pattern: Pattern to block
        """
        self.blocked_patterns.add(pattern)

    def add_required_keyword(self, keyword: str) -> None:
        """Add a required keyword.

        Args:
            keyword: Keyword to require
        """
        self.required_keywords.add(keyword)

    def validate_request(self, request: str) -> bool:
        """Validate a request string.

        Args:
            request: Request to validate

        Returns:
            True if request is safe, False otherwise
        """
        # Check for blocked patterns
        for pattern in self.blocked_patterns:
            if pattern.lower() in request.lower():
                logger.warning(f"Request contains blocked pattern: {pattern}")
                return False

        # Check for required keywords
        for keyword in self.required_keywords:
            if keyword.lower() not in request.lower():
                logger.warning(f"Request missing required keyword: {keyword}")
                return False

        return True
