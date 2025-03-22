"""Service for handling chat interactions with the StakingOptimizer agent.

This service maintains the StakingOptimizer instance and processes chat
messages, converting between API models and agent responses.

Attributes:
    blockchain: Mock blockchain state
    agent: StakingOptimizer agent instance
"""

import os
import logging
from typing import Dict, Any, Optional

from ..core.config import get_settings
from ...blockchain import MockBlockchainState, MockStakingContract
from ...agent.base import StakingOptimizerAgent
from ...agent.models import AgentResponse

logger = logging.getLogger(__name__)

class ChatService:
    """Service for handling chat interactions with the StakingOptimizer agent."""
    
    def __init__(self, blockchain: MockBlockchainState, contract: Optional[MockStakingContract] = None, config_path: Optional[str] = None):
        """Initialize chat service.
        
        Args:
            blockchain: Mock blockchain state for the agent
            contract: Optional mock staking contract. If not provided, a new one will be created
            config_path: Optional path to agent config file. If not provided, a default one will be created
        """
        self.blockchain = blockchain
        self.contract = contract or MockStakingContract(blockchain)
        
        # Get settings for agent initialization
        settings = get_settings()
        
        # Set up agent with required config
        if not config_path:
            config_path = os.path.join(
                os.path.dirname(__file__),
                "..",
                "..",
                "config",
                "agent_config.yaml"
            )
            
            # Ensure config directory exists
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            
            # Create default config if it doesn't exist
            if not os.path.exists(config_path):
                with open(config_path, "w") as f:
                    f.write("""
# Default StakingOptimizer agent configuration
model: openai/gpt-4o-2024-11-20
temperature: 0.7
max_tokens: 1000
""")
        
        # Initialize agent with mock private key for testing
        self.agent = StakingOptimizerAgent(
            private_key="0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
            rpc_url="http://localhost:8545",  # Local Ethereum node
            config_path=config_path,
            mock_blockchain=blockchain,
            mock_contract=self.contract
        )
        
        # Create default account if it doesn't exist
        if "0xdefault" not in blockchain.accounts:
            blockchain.create_account("0xdefault", float(10))  # Give default account 10 ETH
            logger.info("Created default account with 10 ETH")
            
        logger.info("Initialized ChatService with StakingOptimizer agent")

    async def process_message(self, message: str) -> AgentResponse:
        """Process a chat message through the agent.
        
        Args:
            message: User's chat message
            
        Returns:
            AgentResponse containing the result
        """
        try:
            # Check for unsafe requests
            if any(unsafe in message.lower() for unsafe in ['sudo', 'rm', 'delete', 'remove', 'drop']):
                return AgentResponse(
                    success=False,
                    message="I cannot process potentially unsafe requests.",
                    error="Unsafe request detected"
                )
            
            # Process message
            return await self.agent.handle_request(message)
        except Exception as e:
            logger.error(f"Error in agent chat: {str(e)}", exc_info=True)
            return AgentResponse(
                success=False,
                message=str(e),
                error=str(e)
            )
