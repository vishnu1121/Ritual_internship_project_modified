"""State management utilities for the StakingOptimizer agent."""
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

from langchain_core.messages import AIMessage, HumanMessage


class ConversationState(BaseModel):
    """State of a conversation with the agent."""
    thread_id: str = Field(..., description="Unique identifier for the conversation thread")
    messages: List[Dict[str, str]] = Field(default_factory=list, description="List of conversation messages")
    context: Dict[str, str] = Field(default_factory=dict, description="Additional context for the conversation")
    last_tool_result: Optional[Dict[str, str]] = Field(None, description="Result of the last tool execution")


def get_conversation_history(state: ConversationState) -> List[Dict[str, str]]:
    """Get formatted conversation history.
    
    Args:
        state: Current conversation state
        
    Returns:
        List of formatted messages
    """
    return state.messages


def add_human_message(state: ConversationState, content: str) -> None:
    """Add a human message to the conversation.
    
    Args:
        state: Current conversation state
        content: Message content
    """
    state.messages.append({
        "role": "user",
        "content": content
    })


def add_ai_message(state: ConversationState, content: str) -> None:
    """Add an AI message to the conversation.
    
    Args:
        state: Current conversation state
        content: Message content
    """
    state.messages.append({
        "role": "assistant",
        "content": content
    })


def add_tool_result(state: ConversationState, result: Dict[str, str]) -> None:
    """Add a tool execution result to the state.
    
    Args:
        state: Current conversation state
        result: Tool execution result
    """
    state.last_tool_result = result


def get_messages_for_llm(state: ConversationState) -> List[HumanMessage | AIMessage]:
    """Get messages formatted for the LLM.
    
    Args:
        state: Current conversation state
        
    Returns:
        List of LangChain message objects
    """
    llm_messages = []
    for msg in state.messages:
        if msg["role"] == "user":
            llm_messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            llm_messages.append(AIMessage(content=msg["content"]))
    return llm_messages
