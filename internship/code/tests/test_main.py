"""Tests for the main module."""

import os
from unittest.mock import patch
from dotenv import load_dotenv
import pytest
from langchain.agents import AgentExecutor

from src.staking_optimizer.main import create_agent, setup_environment


def test_setup_environment_missing_var():
    """Test setup_environment with missing required variable."""
    # Mock load_dotenv to do nothing and clear environment variables
    with patch('src.staking_optimizer.main.load_dotenv', return_value=None), \
         patch.dict(os.environ, {}, clear=True):
        with pytest.raises(ValueError, match="Missing required environment variables: OPENAI_API_KEY"):
            setup_environment()


def test_setup_environment_success():
    """Test setup_environment with all required variables."""
    # Load the real API key from .env
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("OPENAI_API_KEY not set in environment")

    with patch.dict(os.environ, {"OPENAI_API_KEY": api_key}, clear=True):
        env_vars = setup_environment()
        assert "OPENAI_API_KEY" in env_vars


def test_create_agent_not_implemented():
    """Test create_agent raises NotImplementedError."""
    with pytest.raises(NotImplementedError):
        create_agent()
