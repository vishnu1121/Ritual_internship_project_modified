"""StakeMate character implementation.

This module provides the StakeMate character, a friendly assistant that helps
users with their staking operations.
"""
from typing import Any, List

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage


class StakeMateCharacter:
    """StakeMate character for formatting agent responses.

    This class implements the StakeMate character, which adds personality
    and helpful formatting to agent responses.

    Attributes:
        _emoji: The emoji used in StakeMate's responses
        _name: The character's name
    """

    def __init__(self):
        """Initialize the StakeMate character."""
        self._emoji = "🥩"
        self._name = "Stake Mate"

    def format_request(self, request: str) -> List[BaseMessage]:
        """Format a user request with character context.

        Args:
            request: The user's request string

        Returns:
            List of messages with character context
        """
        system_message = SystemMessage(
            content=f"""You are {self._name} {self._emoji}, a friendly and helpful staking assistant.
            You help users optimize their staking positions and execute staking operations.
            Always be friendly and supportive, but also be clear about risks and limitations.
            """
        )
        user_message = HumanMessage(content=request)
        return [system_message, user_message]

    def format_response(self, response: str) -> str:
        """Format an agent response with character personality.

        Args:
            response: The raw agent response

        Returns:
            Formatted response with character elements
        """
        return f"{self._name} {self._emoji}: {response}"

    def get_agent_prompt(self) -> str:
        """Get the agent prompt template.

        Returns:
            The prompt template for the agent
        """
        return f"""You are {self._name} {self._emoji}, a helpful assistant for staking operations.
        
        You can help users with:
        1. Staking tokens
        2. Claiming rewards
        3. Setting up auto-compound strategies
        4. Optimizing gas usage
        5. Monitoring staking positions
        
        Always be clear about:
        - Gas costs and optimization
        - Risks and rewards
        - Time requirements
        - Network conditions
        
        Respond in a friendly and helpful way, using clear language that users can understand.
        """
