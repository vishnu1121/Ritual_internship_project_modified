"""Debug conversation class."""

import os
import sys
import logging

# Add src to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from src.staking_optimizer.character.conversation import StakeMateConversation

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def main():
    """Debug conversation class."""
    # Get OpenAI key
    api_key = os.getenv("OPENAI_API_KEY", "not set")
    logger.debug("OPENAI_API_KEY=%s", api_key)
    
    # Create conversation
    logger.debug("Creating conversation")
    try:
        conversation = StakeMateConversation(openai_api_key=api_key)
        logger.debug("Successfully created conversation")
        
        # Try to process a message
        logger.debug("Processing message")
        response = conversation.process_message("Can you help me stake ETH?")
        logger.debug("Response: %s", response)
    except Exception as e:
        logger.error("Error: %s", str(e), exc_info=True)

if __name__ == "__main__":
    main()
