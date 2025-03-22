"""Mock StakingOptimizer agent for testing."""

from typing import Dict, Any, Optional
from pydantic import BaseModel

class AgentResponse(BaseModel):
    """Response from agent operations."""
    success: bool
    message: str
    error: Optional[str] = None
    action: Optional[Dict[str, Any]] = None

class MockStakingOptimizerAgent:
    """Mock StakingOptimizer agent for testing."""
    
    def __init__(self, **kwargs):
        """Initialize mock agent."""
        self.kwargs = kwargs

    async def handle_request(self, request: str) -> AgentResponse:
        """Handle a request from the user.
        
        Args:
            request: User's request message
            
        Returns:
            AgentResponse containing message and optional action
        """
        if "stake" in request.lower():
            return AgentResponse(
                success=True,
                message="I'll help you stake your tokens",
                action={
                    "type": "stake",
                    "amount": "100",
                    "token": "ETH"
                }
            )
        elif "unstake" in request.lower():
            return AgentResponse(
                success=True,
                message="I'll help you unstake your tokens",
                action={
                    "type": "unstake",
                    "amount": "50",
                    "token": "ETH"
                }
            )
        else:
            return AgentResponse(
                success=True,
                message="I can help you with staking operations. What would you like to do?"
            )
