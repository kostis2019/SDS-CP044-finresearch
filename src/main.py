"""Main orchestration script - DEBUG VERSION"""

from config.settings import validate_config
from agents.financial_crew import build_financial_crew

def main():
    """Main entry point."""
    
    test_inputs = {
        "ticker": "AAPL",
        "investor_mode": "Neutral",
        "analysis_depth": "standard"
    }
    
    print("Step 1: Building crew...")
    crew = build_financial_crew(inputs=test_inputs)
    
    print(f"Step 2: Crew type check: {type(crew)}")
    print(f"Step 3: Crew object: {crew}")
    
    # Check if it's a Crew object
    from crewai import Crew
    if isinstance(crew, Crew):
        print("✅ Crew object is valid!")
        print(f"   - Agents: {len(crew.agents)}")
        print(f"   - Tasks: {len(crew.tasks)}")
    else:
        print(f"❌ ERROR: Expected Crew object, got {type(crew)}")
        print(f"   Value: {crew}")
        return
    
    print("\nStep 4: Executing crew...")
    result = crew.kickoff()
    
    print("\nStep 5: Results:")
    print("=" * 50)
    print(result)
    print("=" * 50)
    
    return result


if __name__ == "__main__":
    validate_config()
    main()