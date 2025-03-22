"""Test configuration and fixtures for the StakingOptimizer project."""

import os
import pytest
from dotenv import load_dotenv

@pytest.fixture(autouse=True)
def env_setup() -> None:
    """Set up test environment variables."""
    # Load environment variables from .env
    load_dotenv()
    
    # Verify OpenAI API key exists
    if not os.getenv("OPENAI_API_KEY"):
        pytest.fail("OPENAI_API_KEY not found in .env file")
