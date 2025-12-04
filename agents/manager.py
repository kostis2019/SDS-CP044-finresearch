"""Manager Agent receives user requestdelegates work to other agents, ensures all findings are complete and consistent, and produces the final polished report.
"""

from crewai import Agent

def build_manager() -> Agent:
    """
    Build the manager agent.

    This agent receives user request, delegates work to other agents, ensures all findings are complete and consistent, and produces the final polished report.

    Returns:
        Configured manager agent
    """ 
    agent = Agent(
        role="Manager",
        goal="Receive user request, delegate work to other agents, ensure all findings are complete an consistent, "
             "and produce the final polished report",
        backstory=(
            "You are an manager agent that receives user request, delegates work to other agents, and "
            "ensures all findings are complete and consistent, and produces the final polished report."
        ),
        verbose=True,
        allow_delegation=True,      # Allow delegation to other agents
    )

    return agent