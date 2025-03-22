"""Safety validator for StakingOptimizer requests.

This module provides validation logic to ensure that user requests are safe
and appropriate before being processed by the agent.
"""
import re
import logging
from typing import List, Optional, Tuple

logger = logging.getLogger(__name__)

class SafetyValidator:
    """Validates user requests for safety and relevance.

    This class implements checks to ensure that user requests don't contain
    harmful content and are related to staking operations.

    Attributes:
        _blocked_patterns: List of regex patterns for blocked content
        _required_keywords: List of keywords that indicate staking relevance
        _max_request_length: Maximum allowed length for user requests
        _safety_score_threshold: Minimum safety score required to pass validation
        _last_error_message: Last error message from validation
    """

    def __init__(self):
        """Initialize the SafetyValidator with default patterns."""
        self._blocked_patterns = [
            # System security
            r"(?i)delete.*file",  # File deletion
            r"(?i)rm\s+-rf",      # Dangerous shell commands
            r"(?i)format.*disk",   # Disk formatting
            r"(?i)sudo",          # Privileged commands
            r"(?i)chmod",         # File permission changes
            r"(?i)chown",         # File ownership changes
            
            # Malicious intent
            r"(?i)hack",          # Malicious intent
            r"(?i)exploit",       # Security exploits
            r"(?i)attack",        # Attack attempts
            r"(?i)steal",         # Theft attempts
            r"(?i)malware",       # Malware-related
            r"(?i)virus",         # Virus-related
            
            # Smart contract security
            r"(?i)reentrancy",    # Reentrancy attacks
            r"(?i)overflow",      # Integer overflow
            r"(?i)underflow",     # Integer underflow
            r"(?i)frontrun",      # Front-running attacks
            r"(?i)backdoor",      # Backdoor attempts
            
            # Network security
            r"(?i)ddos",          # DDoS attacks
            r"(?i)spoof",         # Spoofing attempts
            r"(?i)intercept",     # Network interception
            
            # Data security
            r"(?i)dump.*data",    # Data dumping
            r"(?i)leak.*key",     # Key leakage
            r"(?i)expose.*secret", # Secret exposure
        ]
        
        self._required_keywords = [
            # Core staking operations
            "stake",
            "staking",
            "unstake",
            "compound",
            "reward",
            "validator",
            "delegation",
            
            # Financial terms
            "apr",
            "apy",
            "yield",
            "interest",
            "return",
            
            # Transaction related
            "gas",
            "fee",
            "transaction",
            "balance",
            
            # Time related
            "schedule",
            "period",
            "frequency",
            "interval",
            
            # Actions
            "withdraw",
            "deposit",
            "claim",
            "check",
            "view",
            "monitor"
        ]
        
        # Maximum request length to prevent DoS
        self._max_request_length = 1000
        
        # Minimum safety score (0-1) required to pass validation
        self._safety_score_threshold = 0.7
        
        # Track last error message
        self._last_error_message = None

    def validate_request(self, request: str) -> Tuple[bool, str]:
        """Validate a user request for safety and relevance.

        Args:
            request: The user's natural language request

        Returns:
            tuple[bool, str]: (is_valid, reason)
                - is_valid: True if the request is safe and relevant
                - reason: Description of why validation failed, or "OK" if passed
        """
        # Check request length
        if len(request) > self._max_request_length:
            return False, f"Request too long (max {self._max_request_length} chars)"
            
        # Check for blocked patterns
        blocked_pattern = self._find_blocked_pattern(request)
        if blocked_pattern:
            return False, f"Request contains blocked pattern: {blocked_pattern}"

        # Check for staking relevance
        if not self._is_staking_related(request):
            return False, "Try to ask me about staking related topics. I can also help with "
            
        # Calculate overall safety score
        safety_score = self._calculate_safety_score(request)
        if safety_score < self._safety_score_threshold:
            return False, f"Request failed safety check (score: {safety_score:.2f})"

        return True, "OK"

    def get_last_error_message(self) -> str:
        """Get the last error message from validation.

        Returns:
            str: The last error message, or "Invalid request" if none set
        """
        return self._last_error_message or "Invalid request"

    def _find_blocked_pattern(self, text: str) -> Optional[str]:
        """Find first blocked pattern in text.

        Args:
            text: The text to check

        Returns:
            Optional[str]: The first blocked pattern found, or None if none found
        """
        for pattern in self._blocked_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return pattern
        return None

    def _is_staking_related(self, text: str) -> bool:
        """Check if text is related to staking operations.

        Args:
            text: The text to check

        Returns:
            bool: True if the text contains staking-related keywords
        """
        text = text.lower()
        logger.debug(f"Checking if text is staking related: {text}")
        logger.debug(f"Required keywords: {self._required_keywords}")
        result = any(keyword.lower() in text for keyword in self._required_keywords)
        logger.debug(f"Is staking related: {result}")
        return result

    def _calculate_safety_score(self, text: str) -> float:
        """Calculate a safety score for the text.

        This implements a simple scoring system based on:
        1. Presence of blocked patterns (major negative impact)
        2. Presence of required keywords (positive impact)
        3. Text complexity and length (minor negative impact)
        4. Special character ratio (negative impact)
        5. Repetitive content (negative impact)

        Args:
            text: The text to analyze

        Returns:
            float: Safety score between 0 and 1
        """
        score = 1.0
        
        # Check for blocked patterns (major negative impact)
        if self._find_blocked_pattern(text):
            score *= 0.1
            
        # Check for required keywords (positive impact)
        keyword_count = sum(1 for keyword in self._required_keywords 
                          if keyword.lower() in text.lower())
        keyword_score = min(keyword_count / 3, 1.0)  # Cap at 1.0
        score *= 0.7 + (0.3 * keyword_score)
        
        # Check text complexity (minor negative impact)
        words = text.split()
        if len(words) > 50:  # Penalize very long requests
            score *= 0.8  # More aggressive penalty
            
        # Check for repetitive content
        unique_words = set(words)
        repetition_ratio = len(unique_words) / len(words)
        if repetition_ratio < 0.5:  # More than 50% repetition
            score *= 0.7  # Significant penalty for repetitive content
            
        # Check special character ratio (negative impact)
        special_chars = sum(1 for c in text if not c.isalnum() and not c.isspace())
        special_ratio = special_chars / len(text)
        if special_ratio > 0.1:  # Penalize high special character ratio
            score *= 0.8
            
        return max(0.0, min(1.0, score))  # Ensure score is between 0 and 1

    def add_blocked_pattern(self, pattern: str) -> None:
        """Add a new pattern to the blocked list.

        Args:
            pattern: Regex pattern to block
        """
        if pattern not in self._blocked_patterns:
            self._blocked_patterns.append(pattern)

    def add_required_keyword(self, keyword: str) -> None:
        """Add a new keyword to the required list.

        Args:
            keyword: Keyword that indicates staking relevance
        """
        if keyword not in self._required_keywords:
            self._required_keywords.append(keyword)
