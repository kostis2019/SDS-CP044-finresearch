"""
Configuration settings for FinResearch AI system.
Manages environment variables and application settings.
"""

import os
from typing import Optional
from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Load environment variables
load_dotenv()


class Settings(BaseModel):
    """Application settings loaded from environment variables."""

    # OpenAI Configuration
    openai_api_key: str = Field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    openai_model: str = Field(default_factory=lambda: os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview"))
    embedding_model: str = Field(default_factory=lambda: os.getenv("EMBEDDING_MODEL", "text-embedding-3-small"))

    # Search API Configuration
    tavily_api_key: Optional[str] = Field(default_factory=lambda: os.getenv("TAVILY_API_KEY"))
    serpapi_api_key: Optional[str] = Field(default_factory=lambda: os.getenv("SERPAPI_API_KEY"))

    # Financial API Configuration
    alphavantage_api_key: Optional[str] = Field(default_factory=lambda: os.getenv("ALPHAVANTAGE_API_KEY"))
    fmp_api_key: Optional[str] = Field(default_factory=lambda: os.getenv("FMP_API_KEY"))
    finnhub_api_key: Optional[str] = Field(default_factory=lambda: os.getenv("FINNHUB_API_KEY"))

    # System Configuration
    max_tokens: int = Field(default_factory=lambda: int(os.getenv("MAX_TOKENS", "4000")))
    temperature: float = Field(default_factory=lambda: float(os.getenv("TEMPERATURE", "0.7")))
    vector_db_path: str = Field(default_factory=lambda: os.getenv("VECTOR_DB_PATH", "./chroma_db"))

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    def validate_required_keys(self) -> None:
        """Validate that required API keys are present."""
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required")

        if not self.tavily_api_key and not self.serpapi_api_key:
            print("Warning: No search API key found. Using limited search capabilities.")

        if not self.alphavantage_api_key and not self.fmp_api_key and not self.finnhub_api_key:
            print("Warning: No financial API key found. Will use yfinance (free, limited).")


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get or create the global settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings()
        _settings.validate_required_keys()
    return _settings
