"""Response formatting for Stake Mate character.

This module handles the formatting of responses to ensure consistency
in style, emoji usage, and markdown formatting.
"""

import re
from typing import Dict, List, Optional
from .prompt_template import get_emoji

def format_response(response: str) -> str:
    """Format the AI's response for consistency and readability.
    
    Args:
        response: Raw response from the language model
        
    Returns:
        str: Formatted response with appropriate styling
    """
    # Add appropriate emojis based on content
    response = _add_emojis(response)
    
    # Ensure proper markdown formatting
    response = _format_markdown(response)
    
    # Clean up any extra whitespace
    response = _clean_whitespace(response)
    
    return response

def _add_emojis(text: str) -> str:
    """Add appropriate emojis based on message content.
    
    Args:
        text: Original text
        
    Returns:
        str: Text with added emojis
    """
    # Add emojis for common actions/states
    patterns = {
        r'\b(stake|staking)\b': get_emoji('stake'),
        r'\b(unstake|unstaking)\b': get_emoji('unstake'),
        r'\b(reward|rewards)\b': get_emoji('rewards'),
        r'\b(gas|fees?)\b': get_emoji('gas'),
        r'\b(error|failed|failure)\b': get_emoji('error'),
        r'\b(success|successful|succeeded)\b': get_emoji('success'),
        r'\b(warning|caution|careful)\b': get_emoji('warning'),
    }
    
    for pattern, emoji in patterns.items():
        if re.search(pattern, text, re.IGNORECASE) and not text.startswith(emoji):
            text = f"{emoji} {text}"
    
    return text

def _format_markdown(text: str) -> str:
    """Ensure proper markdown formatting.
    
    Args:
        text: Original text
        
    Returns:
        str: Text with proper markdown formatting
    """
    # Ensure code blocks are properly formatted
    text = re.sub(r'```(\w+)?\s*(.*?)\s*```', r'```\1\n\2\n```', text, flags=re.DOTALL)
    
    # Ensure inline code is properly formatted
    text = re.sub(r'(?<!`)`([^`]+)`(?!`)', r'`\1`', text)
    
    # Ensure lists are properly formatted
    text = re.sub(r'^(\d+)\.\s*', r'\1. ', text, flags=re.MULTILINE)
    text = re.sub(r'^[-*]\s*', '- ', text, flags=re.MULTILINE)
    
    return text

def _clean_whitespace(text: str) -> str:
    """Clean whitespace in text.
    
    Args:
        text: Text to clean
        
    Returns:
        Cleaned text
    """
    # Replace multiple newlines with double newlines
    text = re.sub(r'\n{3,}', '\n\n', text)
    # Replace multiple spaces with a single space
    text = re.sub(r' +', ' ', text)
    # Remove trailing spaces at end of lines
    text = re.sub(r' +\n', '\n', text)
    # Remove trailing spaces at end of text
    return text.strip()
