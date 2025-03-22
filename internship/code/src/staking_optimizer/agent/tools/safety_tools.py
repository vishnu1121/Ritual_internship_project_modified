"""Tools for validating request safety."""
from typing import Dict, List, Literal

from langchain.tools import BaseTool

from ...safety.validator import SafetyValidator


def create_safety_tools(validator: SafetyValidator) -> List[BaseTool]:
    """Create tools for safety validation.
    
    Args:
        validator: Safety validator instance
        
    Returns:
        List of LangChain tools for safety checks
    """
    return [ValidateRequestTool(validator=validator)]


class ValidateRequestTool(BaseTool):
    """Tool for validating user requests."""
    
    name: str = "validate_request"
    description: str = """
    Validate a user request for safety and staking relevance.
    
    Args:
        request: The user's request to validate
        
    Returns:
        Dict containing:
        - is_safe: Whether the request is safe
        - message: Reason for validation result
    """
    
    def __init__(self, validator: SafetyValidator):
        """Initialize the tool.
        
        Args:
            validator: Safety validator instance
        """
        super().__init__()
        self._validator = validator
        
    def _run(self, request: str) -> Dict[str, str]:
        """Run the validation."""
        is_valid, reason = self._validator.validate_request(request)
        return {
            "is_safe": is_valid,
            "message": reason
        }
        
    async def _arun(self, request: str) -> Dict[str, str]:
        """Async run not implemented."""
        return self._run(request)


class AddBlockedPatternTool(BaseTool):
    """Tool for adding blocked patterns."""
    
    name: str = "add_blocked_pattern"
    description: str = """
    Add a new pattern to block in user requests.
    
    Args:
        pattern: Regular expression pattern to block
        
    Returns:
        Dict containing confirmation message
    """
    
    def __init__(self, validator: SafetyValidator):
        """Initialize the tool.
        
        Args:
            validator: Safety validator instance
        """
        super().__init__()
        self._validator = validator
        
    def _run(self, pattern: str) -> Dict[str, str]:
        """Add the pattern.
        
        Args:
            pattern: Pattern to block
            
        Returns:
            Dict with confirmation
        """
        self._validator.add_blocked_pattern(pattern)
        return {"message": f"Added blocked pattern: {pattern}"}
        
    async def _arun(self, pattern: str) -> Dict[str, str]:
        """Async run not implemented."""
        return self._run(pattern)


class AddRequiredKeywordTool(BaseTool):
    """Tool for adding required keywords."""
    
    name: str = "add_required_keyword"
    description: str = """
    Add a new keyword that indicates staking relevance.
    
    Args:
        keyword: Keyword to require
        
    Returns:
        Dict containing confirmation message
    """
    
    def __init__(self, validator: SafetyValidator):
        """Initialize the tool.
        
        Args:
            validator: Safety validator instance
        """
        super().__init__()
        self._validator = validator
        
    def _run(self, keyword: str) -> Dict[str, str]:
        """Add the keyword.
        
        Args:
            keyword: Keyword to require
            
        Returns:
            Dict with confirmation
        """
        self._validator.add_required_keyword(keyword)
        return {"message": f"Added required keyword: {keyword}"}
        
    async def _arun(self, keyword: str) -> Dict[str, str]:
        """Async run not implemented."""
        return self._run(keyword)
