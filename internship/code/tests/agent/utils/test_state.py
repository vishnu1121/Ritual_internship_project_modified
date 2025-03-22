"""Tests for state management utilities."""
import pytest
from langchain_core.messages import AIMessage, HumanMessage

from src.staking_optimizer.agent.utils.state import (
    ConversationState,
    get_conversation_history,
    add_human_message,
    add_ai_message,
    add_tool_result,
    get_messages_for_llm,
)


@pytest.fixture
def conversation_state():
    """Create a conversation state for testing."""
    return ConversationState(thread_id="test_thread")


def test_conversation_state_initialization():
    """Test conversation state initialization."""
    state = ConversationState(thread_id="test_thread")
    assert state.thread_id == "test_thread"
    assert state.messages == []
    assert state.context == {}
    assert state.last_tool_result is None


def test_get_conversation_history(conversation_state):
    """Test getting conversation history."""
    # Add some messages
    add_human_message(conversation_state, "Hello")
    add_ai_message(conversation_state, "Hi there!")
    
    history = get_conversation_history(conversation_state)
    assert len(history) == 2
    assert history[0]["role"] == "user"
    assert history[0]["content"] == "Hello"
    assert history[1]["role"] == "assistant"
    assert history[1]["content"] == "Hi there!"


def test_add_human_message(conversation_state):
    """Test adding human messages."""
    add_human_message(conversation_state, "Test message")
    assert len(conversation_state.messages) == 1
    assert conversation_state.messages[0]["role"] == "user"
    assert conversation_state.messages[0]["content"] == "Test message"


def test_add_ai_message(conversation_state):
    """Test adding AI messages."""
    add_ai_message(conversation_state, "Test response")
    assert len(conversation_state.messages) == 1
    assert conversation_state.messages[0]["role"] == "assistant"
    assert conversation_state.messages[0]["content"] == "Test response"


def test_add_tool_result(conversation_state):
    """Test adding tool results."""
    result = {"status": "success", "data": "test"}
    add_tool_result(conversation_state, result)
    assert conversation_state.last_tool_result == result


def test_get_messages_for_llm(conversation_state):
    """Test getting messages formatted for LLM."""
    # Add mixed messages
    add_human_message(conversation_state, "Hello")
    add_ai_message(conversation_state, "Hi there!")
    add_human_message(conversation_state, "How are you?")
    
    llm_messages = get_messages_for_llm(conversation_state)
    assert len(llm_messages) == 3
    assert isinstance(llm_messages[0], HumanMessage)
    assert isinstance(llm_messages[1], AIMessage)
    assert isinstance(llm_messages[2], HumanMessage)
    assert llm_messages[0].content == "Hello"
    assert llm_messages[1].content == "Hi there!"
    assert llm_messages[2].content == "How are you?"
