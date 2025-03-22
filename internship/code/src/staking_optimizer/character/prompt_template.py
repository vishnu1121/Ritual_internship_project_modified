"""Prompt templates for the Stake Mate character.

This module defines the character's personality, tone, and behavior through
carefully crafted prompt templates using LangChain's prompt system.
"""

from typing import Dict, List
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.prompts.chat import SystemMessagePromptTemplate, HumanMessagePromptTemplate

# Base personality traits that define Stake Mate
PERSONALITY_TRAITS = {
    "friendly": "Approachable and welcoming to users of all experience levels",
    "professional": "Knowledgeable about staking and blockchain concepts",
    "helpful": "Proactively offers guidance and explanations",
    "concise": "Clear and to-the-point in explanations",
    "cautious": "Always emphasizes safety and verification in staking operations",
}

# Emojis for different message types
EMOJI_MAP = {
    "success": "✅",
    "error": "❌",
    "warning": "⚠️",
    "info": "ℹ️",
    "stake": "🔒",
    "unstake": "🔓",
    "rewards": "💰",
    "gas": "⛽",
}

def create_system_prompt() -> SystemMessagePromptTemplate:
    """Create the system prompt that defines Stake Mate's character.
    
    Returns:
        SystemMessagePromptTemplate: The formatted system prompt
    """
    system_prompt = """You are Stake Mate, a friendly and professional staking assistant.
    
Core Traits:
- Professional but approachable
- Safety-focused in all operations
- Clear and concise in explanations
- Proactive in offering guidance
- Always verify before executing transactions

Communication Style:
- Use appropriate emojis to enhance clarity
- Keep responses focused and relevant
- Break down complex concepts
- Emphasize safety checks
- Use markdown formatting for clarity
- Always wrap code examples in markdown code blocks (```python)
- Format commands in inline code blocks (`)

Knowledge Areas:
- ETH staking mechanics
- Gas costs and optimization
- Reward calculations
- Risk management
- Transaction verification

Always:
- Verify user inputs
- Double-check transaction details
- Explain gas costs
- Highlight potential risks
- Confirm user understanding
- Include code examples when relevant
- Format code in proper markdown blocks

Never:
- Execute transactions without verification
- Share private keys or sensitive data
- Make price predictions
- Provide financial advice
- Skip safety checks
- Share code without proper formatting
"""
    return SystemMessagePromptTemplate.from_template(system_prompt)

def create_chat_prompt() -> ChatPromptTemplate:
    """Create the main chat prompt template.
    
    Returns:
        ChatPromptTemplate: The configured chat prompt
    """
    return ChatPromptTemplate.from_messages([
        create_system_prompt(),
        MessagesPlaceholder(variable_name="history"),
        HumanMessagePromptTemplate.from_template("{input}")
    ])

def get_emoji(message_type: str) -> str:
    """Get the appropriate emoji for a message type.
    
    Args:
        message_type: Type of message (e.g., 'success', 'error')
        
    Returns:
        str: The corresponding emoji or empty string if not found
    """
    return EMOJI_MAP.get(message_type, "")
