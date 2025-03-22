"""Debug OpenAI configuration."""

import os
import logging
from openai import OpenAI
from langchain_openai import ChatOpenAI

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def main():
    """Debug OpenAI configuration."""
    # Print environment variables
    logger.debug("Environment variables:")
    for key, value in os.environ.items():
        if "openai" in key.lower() or "proxy" in key.lower():
            logger.debug("%s=%s", key, value)
            
    # Try to create OpenAI client directly
    logger.debug("Creating OpenAI client directly")
    try:
        client = OpenAI()
        logger.debug("OpenAI client created successfully")
        logger.debug("Client config: %s", client._config)
    except Exception as e:
        logger.error("Failed to create OpenAI client: %s", str(e))
        
    # Try to create ChatOpenAI
    logger.debug("Creating ChatOpenAI")
    try:
        chat = ChatOpenAI()
        logger.debug("ChatOpenAI created successfully")
    except Exception as e:
        logger.error("Failed to create ChatOpenAI: %s", str(e))

if __name__ == "__main__":
    main()
