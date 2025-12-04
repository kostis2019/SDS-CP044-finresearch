"""Main orchestration script for the multi-agent fintech research system."""

from config.settings import validate_config
from agents.financial_crew import build_financial_crew

def main():
    """Main entry point."""
    crew = build_financial_crew()
    result = crew.kickoff()
    print(result)


if __name__ == "__main__":
    # Validate config
    validate_config()

   # Run the main function
    main()
