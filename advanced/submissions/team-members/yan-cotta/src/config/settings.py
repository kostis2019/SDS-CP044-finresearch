"""
Application settings and configuration management.

This module provides centralized configuration using Pydantic for validation
and environment variable loading.
"""

import logging
import os
from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings with environment variable support.
    
    All settings can be overridden via environment variables.
    """
    
    # API Keys - supports both OPENAI_API_KEY and FINRESEARCH_OPENAI_API_KEY
    openai_api_key: str = Field(
        default="",
        description="OpenAI API key for LLM access"
    )
    
    @field_validator('openai_api_key', mode='before')
    @classmethod
    def get_openai_key(cls, v: str) -> str:
        """Try to get OpenAI key from multiple env var names."""
        if v:
            return v
        # Fall back to standard OPENAI_API_KEY if prefixed version not set
        return os.getenv('OPENAI_API_KEY', '')
    
    # Model Configuration
    manager_model: str = Field(
        default="gpt-4o-mini",
        description="Model for the Manager agent (requires strong reasoning)"
    )
    worker_model: str = Field(
        default="gpt-3.5-turbo",
        description="Model for worker agents (Researcher, Analyst, Reporter)"
    )
    
    # Temperature Settings
    manager_temperature: float = Field(
        default=0.1,
        ge=0.0,
        le=2.0,
        description="Temperature for Manager (low for consistent delegation)"
    )
    researcher_temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Temperature for Researcher (higher for creative synthesis)"
    )
    analyst_temperature: float = Field(
        default=0.0,
        ge=0.0,
        le=2.0,
        description="Temperature for Analyst (zero for numerical precision)"
    )
    reporter_temperature: float = Field(
        default=0.5,
        ge=0.0,
        le=2.0,
        description="Temperature for Reporter (balanced for structured writing)"
    )
    
    # Memory / ChromaDB Configuration
    chroma_persist_dir: str = Field(
        default=".chroma_db",
        description="Directory for ChromaDB persistence"
    )
    chroma_collection_name: str = Field(
        default="finresearch_memory",
        description="ChromaDB collection name"
    )
    
    # Output Configuration
    output_dir: str = Field(
        default="./outputs",
        description="Directory for generated reports and artifacts"
    )
    
    # Report Quality Settings
    min_executive_summary_length: int = Field(
        default=100,
        ge=50,
        le=500,
        description="Minimum character length for executive summary"
    )
    min_section_length: int = Field(
        default=50,
        ge=20,
        le=200,
        description="Minimum character length for report sections"
    )
    required_report_sections: list[str] = Field(
        default=[
            "Executive Summary",
            "Market Data",
            "News Analysis",
            "Risk Assessment",
        ],
        description="Required section headers in final report"
    )
    
    # Logging
    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR)"
    )
    log_file: Optional[str] = Field(
        default=None,
        description="Log file path (None for stdout only)"
    )
    log_chain_of_thought: bool = Field(
        default=True,
        description="Whether to log agent chain-of-thought reasoning"
    )
    
    # Request Configuration
    max_news_results: int = Field(
        default=10,
        ge=1,
        le=50,
        description="Maximum news articles to retrieve"
    )
    request_timeout: int = Field(
        default=30,
        ge=5,
        le=120,
        description="Timeout for external API requests in seconds"
    )
    
    class Config:
        """Pydantic configuration."""
        env_prefix = "FINRESEARCH_"
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    @property
    def chroma_path(self) -> Path:
        """Get the ChromaDB persistence path as a Path object."""
        return Path(self.chroma_persist_dir)
    
    @property
    def output_path(self) -> Path:
        """Get the output directory as a Path object, creating if needed."""
        path = Path(self.output_dir)
        path.mkdir(parents=True, exist_ok=True)
        return path


def setup_logging(
    level: Optional[str] = None,
    log_file: Optional[str] = None,
    log_chain_of_thought: bool = True
) -> logging.Logger:
    """
    Configure application logging with chain-of-thought support.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional file path for logging output
        log_chain_of_thought: Whether to enable verbose agent logging
        
    Returns:
        Configured root logger
    """
    settings = get_settings()
    level = level or settings.log_level
    log_file = log_file or settings.log_file
    
    log_format = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    handlers: list[logging.Handler] = []
    handlers.append(logging.StreamHandler())
    
    if log_file:
        handlers.append(logging.FileHandler(log_file))
    
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=log_format,
        datefmt=date_format,
        handlers=handlers,
        force=True
    )
    
    # Configure third-party library logging
    if not log_chain_of_thought:
        logging.getLogger("crewai").setLevel(logging.WARNING)
        logging.getLogger("langchain").setLevel(logging.WARNING)
    
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("chromadb").setLevel(logging.WARNING)
    
    return logging.getLogger()


def get_logger(name: str) -> logging.Logger:
    """
    Get a named logger for a module.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached application settings.
    
    Loads .env file from multiple possible locations before creating settings.
    
    Returns:
        Settings instance (cached for performance)
    """
    from dotenv import load_dotenv
    
    # Try loading .env from various locations
    possible_env_paths = [
        Path.cwd() / ".env",  # Current working directory
        Path(__file__).parent.parent.parent / ".env",  # Project root (yan-cotta/)
        Path(__file__).parent.parent.parent.parent.parent.parent.parent / ".env",  # Workspace root
    ]
    
    for env_path in possible_env_paths:
        if env_path.exists():
            load_dotenv(env_path)
            break
    
    return Settings()


def clear_settings_cache() -> None:
    """Clear the settings cache to reload configuration."""
    get_settings.cache_clear()


# Paths relative to this module
CONFIG_DIR = Path(__file__).parent
AGENTS_CONFIG_PATH = CONFIG_DIR / "agents.yaml"
TASKS_CONFIG_PATH = CONFIG_DIR / "tasks.yaml"
