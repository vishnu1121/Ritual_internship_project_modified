"""Tests for the StakeMate conversation handler."""

import logging
import pytest
from langchain.schema import AIMessage, HumanMessage

from src.staking_optimizer.character.conversation import StakeMateConversation
from src.staking_optimizer.character.prompt_template import get_emoji

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@pytest.fixture
def conversation():
    """Create a StakeMateConversation instance for testing."""
    logger.debug("Creating conversation fixture")
    try:
        conv = StakeMateConversation()
        logger.debug("Successfully created conversation")
        return conv
    except Exception as e:
        logger.error("Failed to create conversation: %s", str(e), exc_info=True)
        raise

def test_process_message_with_context(conversation):
    """Test message processing with additional context."""
    # Process message with context
    context = {"wallet_balance": "1.5 ETH"}
    response = conversation.process_message("Hello", context)
    
    # Verify response
    assert isinstance(response, str)
    assert len(response) > 0

def test_process_message_error_handling(conversation):
    """Test error handling in message processing."""
    # Process message with invalid context to trigger error
    context = {"invalid": None}
    response = conversation.process_message("Hello", context)
    
    # Verify response still works
    assert isinstance(response, str)
    assert len(response) > 0

def test_memory_management(conversation):
    """Test conversation memory management."""
    # Store some interactions
    conversation._store_interaction("Hello", "Hi there!")
    conversation._store_interaction("How are you?", "I'm good!")
    
    # Verify memory contains the interactions
    memory_vars = conversation.memory.load_memory_variables({})
    assert len(memory_vars["history"]) == 4  # 2 messages each for human and AI
    
    # Clear memory
    conversation.clear_memory()
    memory_vars = conversation.memory.load_memory_variables({})
    assert len(memory_vars["history"]) == 0

def test_emoji_consistency(conversation):
    """Test emoji usage in responses."""
    # Test stake-related message
    response = conversation.process_message("Can you help me stake ETH?")
    assert get_emoji('stake') in response
    
    # Test general message
    response = conversation.process_message("Hello!")
    assert len(response) > 0

def test_markdown_formatting(conversation):
    """Test markdown formatting in responses."""
    # Test code-related query
    response = conversation.process_message("Can you show me how to stake ETH in Python?")
    assert "```" in response  # Should contain a code block
    
    # Test list-related query
    response = conversation.process_message("What are the steps to stake ETH?")
    assert any(line.strip().startswith(("1.", "-", "*")) for line in response.split("\n"))
