"""Base utilities for loading prompts."""

import os

def load_prompt(filename: str) -> str:
    """
    Load agent system prompt from markdown file.

    Args:
        filename: Name of the prompt file (e.g., 'market_researcher.md')

    Returns:
        Prompt content as string

    Raises:
        FileNotFoundError: If prompt file doesn't exist
    """
    # Get the prompts directory relative to this file
    current_dir = os.path.dirname(__file__)
    #project_root = os.path.dirname(current_dir)
    #prompts_dir = os.path.join(project_root, 'prompts')
    prompts_dir = os.path.join(current_dir, 'prompts')

    filepath = os.path.join(prompts_dir, filename)

    if not os.path.exists(filepath):
        raise FileNotFoundError(
            f"Prompt file not found: {filepath}\n"
            f"Make sure {filename} exists in the prompts/ directory."
        )

    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()