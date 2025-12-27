# llm/llm_factory.py
# Factory for CrewAI-compatible LLM instances
# Note: Signal patching is handled by sitecustomize.py (loaded automatically by Python)
# ---------------------------------------------

import os
from langchain_openai import ChatOpenAI


def get_llm():
    """
    Factory for CrewAI-compatible OpenAI LLM.
    Reads configuration from environment variables.
    
    Environment Variables:
        OPENAI_API_KEY: Required - OpenAI API key
        OPENAI_MODEL: Optional - Model name (default: gpt-4o-mini)
    
    Returns:
        ChatOpenAI: Configured LLM instance
    
    Raises:
        RuntimeError: If OPENAI_API_KEY is not set
    """
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is not set. "
            "Please set it in your .env file or environment variables."
        )

    return ChatOpenAI(
        api_key=api_key,
        model=model,
        temperature=0.2,
    )
