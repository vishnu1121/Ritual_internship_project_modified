"""Conversation handling for Stake Mate character.

This module manages the conversation flow, memory, and context tracking
using LangChain's conversation and memory components.
"""

import logging
import os
from typing import List, Dict, Any, Optional, Union

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.memory import BaseMemory
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory

from .prompt_template import create_chat_prompt, get_emoji
from .response_formatter import format_response

logger = logging.getLogger(__name__)

class StakeMateConversation:
    """A conversation handler for the StakeMate character.
    
    This class handles the conversation flow with the StakeMate character,
    maintaining context and ensuring consistent behavior using LangChain components.
    
    Attributes:
        memory: Conversation memory buffer
        prompt: Chat prompt template
        llm: Language model instance
    """
    
    def __init__(self, model_name: str = "openai/gpt-4o-2024-11-20", openai_api_key: Optional[str] = None):
        """Initialize the StakeMate conversation handler.
        
        Args:
            model_name: Name of the language model to use
            openai_api_key: OpenAI API key
        """
        logger.debug("Initializing StakeMateConversation")
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="output"
        )
        logger.debug("Created memory buffer")
        
        self.prompt = create_chat_prompt()
        logger.debug("Created chat prompt")
        
        # Initialize with minimal configuration
        try:
            logger.debug("Initializing ChatOpenAI with model_name=%s", model_name)
            self.llm = ChatOpenAI(
                model_name=model_name,
                temperature=0.7,  # Balance between creativity and consistency
                streaming=False,  # For simplicity in initial implementation
                request_timeout=60,  # Reasonable timeout for staking operations
                openai_api_key=openai_api_key,
                base_url=os.getenv("OPENAI_BASE_URL", "https://openrouter.ai/api/v1")
            )
            logger.debug("Successfully initialized ChatOpenAI")
        except Exception as e:
            logger.error("Failed to initialize ChatOpenAI: %s", str(e), exc_info=True)
            raise
            
        logger.info("Initialized StakeMateConversation with model: %s", model_name)
    
    def process_message(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Process a user message and generate a response.
        
        Args:
            message: User's input message
            context: Optional context dictionary (e.g., wallet state)
            
        Returns:
            str: Formatted response from Stake Mate
        """
        try:
            # Add context to the message if provided
            if context:
                message = self._add_context(message, context)
            
            # Generate response using the language model
            chain = self.prompt | self.llm
            response = chain.invoke({
                "input": message,
                "history": self.memory.load_memory_variables({})["history"]
            })
            
            # Format and store the response
            formatted_response = format_response(response.content)
            self._store_interaction(message, formatted_response)
            
            return formatted_response
            
        except Exception as e:
            logger.error("Error processing message: %s", str(e))
            return f"{get_emoji('error')} I encountered an error processing your message. Please try again."
    
    def _add_context(self, message: str, context: Dict[str, Any]) -> str:
        """Add context to the user's message.
        
        Args:
            message: Original user message
            context: Context dictionary
            
        Returns:
            str: Message with added context
        """
        context_str = "\nContext:\n"
        for key, value in context.items():
            context_str += f"- {key}: {value}\n"
        return f"{message}\n{context_str}"
    
    def _store_interaction(self, user_message: str, ai_response: str) -> None:
        """Store the interaction in memory.
        
        Args:
            user_message: User's message
            ai_response: AI's response
        """
        self.memory.save_context(
            {"input": user_message},
            {"output": ai_response}
        )
    
    def clear_memory(self) -> None:
        """Clear the conversation memory."""
        self.memory.clear()
        logger.info("Cleared conversation memory")
