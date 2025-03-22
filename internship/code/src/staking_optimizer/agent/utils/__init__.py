"""Utilities for the StakingOptimizer agent."""
from .error_handler import ErrorResponse, handle_tool_error
from .state import (
    ConversationState,
    get_conversation_history,
    add_human_message,
    add_ai_message,
    add_tool_result,
    get_messages_for_llm,
)

__all__ = [
    "ErrorResponse",
    "handle_tool_error",
    "ConversationState",
    "get_conversation_history",
    "add_human_message",
    "add_ai_message",
    "add_tool_result",
    "get_messages_for_llm",
]
