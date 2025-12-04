"""Market Researcher performs market research, extracts relevant text snippet and stores results"""

from crewai import Agent, Task, Crew, Process
from crewai.tools import tool
import yfinance as yf
from langchain_openai import ChatOpenAI
from .base import load_prompt

def build_market_researcher() -> Agent:
    """
    Build the market researcher agent.

    This agent performs market research, extracts relevant text snippet and stores results in vector memory. 

    Returns:
        Configured market researcher agent
    """
    
    # Load system prompt
    prompt = load_prompt('market_researcher.md')

    agent = Agent(
        role="Market Researcher",
        goal="performs market research, extracts relevant text snippet and stores results",
        backstory=(prompt),
        verbose=True, 
        # ALLOW DELEGATION: Set to False because we want this agent to do the
        # research itself, not delegate to the writer (who has no tools anyway).
        allow_delegation=False,
        
       # LLM: We use temperature=0.7 for more creative, engaging writing
        # while still maintaining coherence and accuracy.
        llm=ChatOpenAI(model_name="gpt-4", temperature=0.7)
    )

    return agent

def build_market_researcher_task() -> Task:
    """
    Build market_researcher task:

    1 Searches markets, news, press releases, and analyst commentary
    2 Extracts relevant text snippets
    3 Stores results in vector memory
   
    Returns:
        Configured market research task
    """
    task = Task(
       description=(
        "You are market researcher who performs the tasks: \n"
        " 1 Searches markets, news, press releases, and analyst commentary\n "
        " 2 Extracts relevant text snippets\n"
        " 3 Stores results in vector memory"
    ),
    expected_output=(
        "A  market research report in professional format with:\n"
        "- A compelling headline\n"
        "- Financial market news, press releases and analyst commentary \n"
        "- Brief analysis\n"
        "- Closing thought"
    ),
    agent=build_market_researcher()    
    )

    return task