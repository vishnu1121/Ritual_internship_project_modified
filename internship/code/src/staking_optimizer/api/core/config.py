"""API configuration settings.

This module manages configuration for the StakingOptimizer API, including
environment variables, logging setup, and other settings.
"""

import logging
import os
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """API settings loaded from environment variables.
    
    Attributes:
        app_name: Name of the application
        debug: Debug mode flag
        api_prefix: Prefix for all API routes
        logging_level: Minimum logging level
        OPENAI_API_KEY: OpenAI API key for agent (use an OpenRouter key instead)
        OPENAI_BASE_URL: OpenAI base URL for agent
    """
    # API settings
    app_name: str = "StakingOptimizer API"
    debug: bool = False
    api_prefix: str = "/api/v1"
    logging_level: str = "INFO"
    
    # Agent settings
    OPENAI_API_KEY: str  # use an OpenRouter key instead
    OPENAI_BASE_URL: str = "https://openrouter.ai/api/v1"

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="allow"  # Allow extra fields from environment
    )

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance.
    
    Returns:
        Settings object with configuration values.
    """
    return Settings()

def setup_logging():
    """Configure logging for the API.
    
    Sets up logging with appropriate format and level based on settings.
    """
    settings = get_settings()
    
    logging.basicConfig(
        level=getattr(logging, settings.logging_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Create logger for this module
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured at {settings.logging_level} level")
