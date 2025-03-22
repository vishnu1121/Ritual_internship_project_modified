"""Tests for the response formatter."""

import pytest
from src.staking_optimizer.character.response_formatter import (
    format_response,
    _add_emojis,
    _format_markdown,
    _clean_whitespace
)
from src.staking_optimizer.character.prompt_template import get_emoji

def test_emoji_addition():
    """Test emoji addition to responses."""
    # Test stake emoji
    text = "Your stake has been confirmed"
    result = _add_emojis(text)
    assert get_emoji('stake') in result
    
    # Test multiple emojis
    text = "Stake successful, rewards available"
    result = _add_emojis(text)
    assert get_emoji('stake') in result
    assert get_emoji('rewards') in result
    
    # Test case insensitivity
    text = "STAKING in progress"
    result = _add_emojis(text)
    assert get_emoji('stake') in result

def test_markdown_formatting():
    """Test markdown formatting."""
    # Test code block formatting
    text = "```python print('hello')```"
    result = _format_markdown(text)
    assert "```python\nprint('hello')\n```" in result
    
    # Test inline code formatting
    text = "Use `print()` function"
    result = _format_markdown(text)
    assert "`print()`" in result
    
    # Test list formatting
    text = "1.First\n2.Second"
    result = _format_markdown(text)
    assert "1. First" in result
    assert "2. Second" in result

def test_whitespace_cleaning():
    """Test whitespace cleaning."""
    # Test multiple newlines
    text = "Hello\n\n\n\nWorld"
    result = _clean_whitespace(text)
    assert "Hello\n\nWorld" == result
    
    # Test trailing whitespace
    text = "Hello  \nWorld  "
    result = _clean_whitespace(text)
    assert "Hello\nWorld" == result
    
    # Test sentence spacing
    text = "Hello.\n\n\nWorld!"
    result = _clean_whitespace(text)
    assert "Hello.\n\nWorld!" == result

def test_complete_formatting():
    """Test complete response formatting."""
    text = """```python
print('stake tokens')
```

Your stake   was successful!


Rewards are ready.   """
    
    result = format_response(text)
    
    # Check emoji addition
    assert get_emoji('stake') in result
    assert get_emoji('rewards') in result
    
    # Check markdown formatting
    assert "```python" in result
    assert "```" in result
    
    # Check whitespace cleaning
    assert "\n\n\n" not in result
    assert "successful!   " not in result
