# run_crew.py
# CLI runner script for the pure CrewAI FinResearch implementation
# This is a CLI ENTRY POINT - load_dotenv() is called here
# ---------------------------------------------

from dotenv import load_dotenv

# Load environment variables at CLI entry point
load_dotenv()

import os
import sys
from llm.llm_factory import get_llm
from crews.finresearch_crew import FinResearchCrew
from tools.sector_detection import detect_sector


def validate_environment():
    """Validate required environment variables before running."""
    required = ["OPENAI_API_KEY"]
    missing = [k for k in required if not os.getenv(k)]
    
    if missing:
        print(f"ERROR: Missing required environment variables: {', '.join(missing)}")
        print("Please set these in your .env file or environment.")
        sys.exit(1)
    
    optional = ["TAVILY_API_KEY", "SERPAPI_API_KEY"]
    missing_optional = [k for k in optional if not os.getenv(k)]
    if missing_optional:
        print(f"WARNING: Missing optional API keys: {', '.join(missing_optional)}")
        print("News search functionality may not work.\n")


def main(ticker: str = "AAPL"):
    """
    Run the pure CrewAI FinResearch pipeline with auto sector detection.
    
    Args:
        ticker: Stock ticker symbol to analyze (default: AAPL)
    """
    
    print("=" * 60)
    print("FinResearch AI - Pure CrewAI with Auto Sector Detection")
    print("=" * 60)
    
    # Validate environment
    validate_environment()
    
    # Auto-detect sector
    mapped_sector, raw_sector = detect_sector(ticker)
    
    print(f"\nAnalyzing: {ticker}")
    print(f"Detected Sector: {mapped_sector}")
    if raw_sector and raw_sector != mapped_sector:
        print(f"  (Yahoo Finance: {raw_sector})")
    print("-" * 60)
    
    # Initialize
    llm = get_llm()
    crew = FinResearchCrew(llm)
    
    # Run the full pipeline
    print("\nStarting CrewAI execution...")
    print("   - Analyst and Researcher will run in parallel")
    print("   - Reporter will synthesize the final report")
    print("-" * 60)
    
    result = crew.run(
        ticker=ticker,
        sector=mapped_sector,
    )
    
    # Display results
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    
    print(f"\nTicker: {result.get('ticker', ticker)}")
    print(f"Sector: {mapped_sector}")
    print(f"As of: {result.get('as_of_date', 'N/A')}")
    print(f"Final Score: {result.get('final_score', 'N/A')}")
    print(f"Rating: {result.get('rating_5_tier', 'N/A')}")
    print(f"Confidence: {result.get('confidence', 'N/A')}")
    print(f"Risk Level: {result.get('risk_level', 'N/A')}")
    
    # Check for errors
    if "error" in result:
        print(f"\nERROR: {result['error']}")
        return result
    
    # Print the report
    report_md = result.get('report_markdown', '')
    if report_md:
        print("\n" + "=" * 60)
        print("FULL REPORT")
        print("=" * 60)
        print(report_md)
    else:
        print("\nReport markdown not generated. Raw output:")
        import json
        print(json.dumps(result, indent=2, default=str))
    
    return result


if __name__ == "__main__":
    # Allow ticker to be passed as command line argument
    ticker = sys.argv[1] if len(sys.argv) > 1 else "AAPL"
    main(ticker)
