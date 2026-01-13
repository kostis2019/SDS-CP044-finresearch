"""Configuration management for the investment research system."""

import os
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class ConfigurationError(Exception):
    """Raised when required configuration is missing."""
    pass


def get_config() -> Dict[str, Any]:
    """
    Load and validate configuration from environment variables.

    Returns:
        Dictionary containing all configuration settings

    Raises:
        ConfigurationError: If required API keys are missing
    """

    # Required API keys
    openai_key = os.getenv('OPENAI_API_KEY')
    tavily_key = os.getenv('TAVILY_API_KEY')

    if not openai_key:
        raise ConfigurationError(
            "OPENAI_API_KEY not found. Please set it in your .env file.\n"
            "Copy .env.example to .env and add your API key."
        )

    if not tavily_key:
        raise ConfigurationError(
            "TAVILY_API_KEY not found. Please set it in your .env file.\n"
            "Get a free API key at: https://www.tavily.com/"
        )

    # Model settings with defaults
    config = {
        'openai_api_key': openai_key,
        'tavily_api_key': tavily_key,       
    }

    return config


def validate_config() -> bool:
    """
    Validate that all required configuration is present.

    Returns:
        True if configuration is valid

    Raises:
        ConfigurationError: If configuration is invalid
    """
    try:
        config = get_config()
        return True
    except ConfigurationError as e:
        raise e
