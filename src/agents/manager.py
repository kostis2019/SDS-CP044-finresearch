"""Manager Agent receives user requestdelegates work to other agents, ensures all findings are complete and consistent, and produces the final polished report.
"""

from crewai import Agent

def build_manager(inputs: dict = None) -> Agent:
    """
    Build the manager agent.
    
    This agent receives user request, delegates work to other agents, ensures all findings are complete and consistent, and produces the final polished report.

    Returns:
        Configured manager agent
    """ 
    ticker = inputs.get("ticker") 
    
    agent = Agent(
        role="Manager",
        goal=f"Receive user request, delegate work to other agents, and send the final report to users.",           
        backstory=(
            "You are an manager agent that have following responsibilities:\n\n"
            f"- Receive user request for the stock {ticker}\n"
             "- Route the user request\n"
             "- Delegrate tasks to financial alanyst agent, market researcher agent and reporter agent\n"
             "- Obtain the financial report produced from the market reporter.\n"
             "- Send the final report to the user\n\n"                      
        ),
        verbose=True,
        allow_delegation=True,      # Allow delegation to other agents

        max_iter=5
    )

    return agent