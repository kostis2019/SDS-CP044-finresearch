"""The Financial Crew represents group of agents working together to achieve a set of financial service tasks:
    1. Manager Agent delegates tasks to financial analyst and market researcher and produces final report
    2. Finacial Analyst Agent analyses company-specific financial data
    3. Market Researcher Agent searches markets, extracts relevant text snippets and stores results memory"""

from crewai import Agent, Crew, Process, Task
from langchain_openai import ChatOpenAI
from agents.base import load_prompt
from agents.manager import build_manager
from agents.financial_analyst import build_financial_analyst, build_financial_analyst_task
from agents.market_researcher import build_market_researcher, build_market_researcher_task
from agents.reporter import build_reporter, build_reporter_task

def build_financial_crew(inputs: dict = None) -> Crew:
    """
    Build the financial crew.

    The Financial Crew represents group of agents working together to achieve a set of financial service tasks:
    1. Manager Agent delegates tasks to financial analyst and market researcher and produces final report
    2. Finacial Analyst Agent analyses company-specific financial data
    3. Market Researcher Agent searches markets, extracts relevant text snippets and stores results memory                         
    """ 
    # Validate inputs
    if inputs is None:
        raise ValueError("Inputs are required to build the crew")
    
    ticker = inputs.get("ticker")
    if not ticker:
        raise ValueError("Ticker symbol is required in inputs")
    
    print(f"🔨  Building crew for {ticker}...")

    # Build agents
    financial_analyst = build_financial_analyst()
    market_researcher = build_market_researcher()
    reporter = build_reporter()
       
    # Build tasks
    financial_analyst_task = build_financial_analyst_task(inputs)
    market_researcher_task = build_market_researcher_task(inputs)
    reporter_task = build_reporter_task(inputs, [financial_analyst_task, market_researcher_task])

    # Set parallel tasks as async for financial alanyst and market researcher
    financial_analyst_task.async_execution = True
    market_researcher_task.async_execution = True

    # Have reporter wait for financial analyst and market researcher complete their tasks
    reporter_task.async_execution = False

    crew = Crew(  
        agents=[financial_analyst, market_researcher, reporter],
        tasks=[financial_analyst_task, market_researcher_task, reporter_task],
      
        # Set process as sequential as tasks execution among all agents are performed
        # in hybrid approach:
        # Some tasks sequential (reporter-> async_execution=False)
        # Some tasks parallel (financial analyst and researcher -> async_execution=True)
        process=Process.sequential,

        manager_agent=build_manager(inputs),
        verbose=True           
    )

    return crew