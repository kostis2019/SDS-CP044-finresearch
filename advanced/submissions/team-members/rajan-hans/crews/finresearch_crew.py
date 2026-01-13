# crews/finresearch_crew.py
# CrewAI implementation with Pydantic schema enforcement
# Uses strict JSON schemas to reduce hallucinations
# load_dotenv() called here at application entry point only
# ---------------------------------------------
"""
                ┌─────────────────┐
                │   analyst_task  │ async_execution=True
                │                 │────────────┐
                └─────────────────┘            │
START ──────────►                              ├──► reporter_task (waits for both)
                ┌─────────────────┐            │    context=[analyst, researcher]
                │ researcher_task │ async_execution=True
                │                 │────────────┘
                └─────────────────┘


"""


from datetime import date
from typing import Dict, Any
import json
import re

from crewai import Agent, Task, Crew, Process
from pydantic import ValidationError

# Import CrewAI-wrapped tools
from tools.crewai_tools import ANALYST_TOOLS
from tools.news_tools import (
    search_news_tavily,
    search_news_serpapi,
    search_news_combined,
)

# Import Pydantic schemas for structured outputs
from schemas.analyst_schemas import AnalystOutput, InvestmentScores
from schemas.researcher_schemas import ResearcherOutput, SentimentScore
from schemas.reporter_schemas import ReportOutput, CombinedAnalysisOutput


def safe_json_parse(raw_output: str, default: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Safely parse JSON from LLM output, handling markdown code blocks.
    """
    if default is None:
        default = {}

    if not raw_output:
        return default

    text = raw_output.strip()

    # 1. Strip Markdown Code Blocks
    if text.startswith("```"):
        # Remove first line (```json or ```)
        text = text.split("\n", 1)[1] if "\n" in text else ""
        # Remove last line if it is ```
        if text.rstrip().endswith("```"):
            text = text.rstrip()[:-3]

    text = text.strip()

    # 2. Try direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # 3. Robust Extraction (Find first '{' and last '}')
    start_idx = text.find("{")
    end_idx = text.rfind("}")

    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
        json_candidate = text[start_idx : end_idx + 1]
        try:
            return json.loads(json_candidate)
        except json.JSONDecodeError:
            pass

    return default


class FinResearchCrew:
    """
    Pure CrewAI implementation of the FinResearch multi-agent system.

    Uses Pydantic schemas for strict output validation to prevent hallucinations.

    Architecture:
    - Analyst Agent: Quantitative analysis (fundamentals, technicals, scoring)
    - Researcher Agent: News and sentiment analysis
    - Reporter Agent: Final report generation

    Execution Pattern:
    - Uses sequential process with async_execution=True on parallel tasks
    - Analyst and Researcher tasks run in parallel
    - Reporter task waits for both via context dependencies

    Schema Enforcement:
    - Each task uses output_pydantic parameter for strict typing
    - Reduces risk of LLM hallucinations
    - Provides automatic validation of outputs
    """

    def __init__(self, llm):
        """
        Initialize all agents with their roles, goals, and tools.

        Args:
            llm: LangChain-compatible LLM instance (e.g., ChatOpenAI)
        """
        self.llm = llm
        self._create_agents()

    def _create_agents(self):
        """Create all agents with proper CrewAI configuration."""

        # Analyst Agent - Quantitative analysis specialist
        self.analyst_agent = Agent(
            role="Senior Quantitative Analyst",
            goal=(
                "Produce accurate, data-driven financial analysis using computed metrics "
                "and factor scores. Never invent numbers - always use tool outputs."
            ),
            backstory=(
                "You are a buy-side equity analyst with expertise in quantitative methods. "
                "You specialize in fundamental analysis (financial statements, ratios, growth metrics), "
                "technical analysis (price trends, momentum, volatility), and multi-factor scoring. "
                "You rely strictly on data from your analytical tools and never fabricate figures. "
                "You always return data in the exact JSON structure requested."
            ),
            llm=self.llm,
            tools=ANALYST_TOOLS,
            verbose=True,
        )

        # Researcher Agent - News and sentiment specialist
        self.researcher_agent = Agent(
            role="Market Intelligence Researcher",
            goal=(
                "Gather and synthesize recent market news, events, and sentiment signals "
                "for the target stock. Only report information retrieved from news searches."
            ),
            backstory=(
                "You are a financial journalist turned research analyst. You track breaking news, "
                "earnings announcements, analyst upgrades/downgrades, and market-moving events. "
                "You MUST use your search tools to fetch real, recent news articles. "
                "Start with search_news_combined which automatically tries multiple sources. "
                "Never fabricate headlines or sentiment - only report what you actually retrieve. "
                "If no news is found, return empty lists rather than making up information."
            ),
            llm=self.llm,
            tools=[search_news_combined, search_news_tavily, search_news_serpapi],
            verbose=True,
        )

        # Reporter Agent - Report synthesis specialist
        self.reporter_agent = Agent(
            role="Senior Research Report Writer",
            goal=(
                "Transform analyst and researcher outputs into a professional, "
                "investment-committee-ready equity research report."
            ),
            backstory=(
                "You are a senior equity research associate at a bulge bracket investment bank. "
                "You write clear, structured reports for institutional investors and investment committees. "
                "You NEVER invent facts, figures, or news. You only use information provided by "
                "the Analyst and Researcher. If data is missing, you explicitly state 'Not available'. "
                "You always follow the exact output structure requested."
            ),
            llm=self.llm,
            verbose=True,
        )

    def run(
        self,
        ticker: str,
        sector: str,
        force_refresh: bool = False,
    ) -> Dict[str, Any]:
        """
        Execute the full research pipeline using CrewAI with Pydantic schema enforcement.

        Args:
            ticker: Stock ticker symbol (e.g., 'AAPL')
            sector: Sector for benchmark comparison (e.g., 'Technology')
            force_refresh: If True, bypass caching (reserved for future use)

        Returns:
            Dict containing the full research output including report markdown.
        """

        # =========================================================
        # TASK 1: Quantitative Analysis (Analyst Agent)
        # Uses AnalystOutput Pydantic schema for validation
        # =========================================================
        analyst_task = Task(
            description=f"""
            Perform comprehensive quantitative analysis for {ticker} in the {sector} sector.
            
            You MUST use your tools to gather data. Follow this sequence:
            
            1. Use 'get_company_profile' to get basic company information.
            2. Use 'get_analyst_ratings' to fetch Wall Street consensus and target prices.  <-- ADDED
            3. Use 'compute_investment_scores' to get all scores and metrics.
            
            Based on the tool outputs, provide a structured analysis.
            Ensure you map the 'get_analyst_ratings' output to the 'market_consensus' field.
            
            IMPORTANT: Your output MUST strictly follow the schema. Do not add extra fields.
            Only include data that came from your tools - never invent numbers.
            """,
            agent=self.analyst_agent,
            expected_output=f"Structured analysis for {ticker} with scores, technicals, fundamentals, and analyst ratings.",  # <-- UPDATED
            output_pydantic=AnalystOutput,
            async_execution=True,
        )

        # =========================================================
        # TASK 2: News & Sentiment Research (Researcher Agent)
        # Uses ResearcherOutput Pydantic schema for validation
        # =========================================================
        researcher_task = Task(
            description=f"""
            Research recent market news and sentiment for {ticker}.
            
            CRITICAL INSTRUCTIONS:
            1. Use 'search_news_combined' first.
            2. **ANTI-LOOP RULE:** You are allowed a MAXIMUM of 3 search attempts.
            3. If the tool returns "I tried reusing the same input", **STOP SEARCHING IMMEDIATELY**. Do NOT retry the same query. Use whatever news you have gathered so far.
            4. If no news is found after your attempts, return empty lists. Do NOT make up headlines.
            5. If tools return errors about API keys, note that in your response.
            
            After retrieving news, analyze and synthesize:
            - 3-5 key headlines/developments from the past week
            - Overall sentiment (Positive/Neutral/Negative)
            - Key risks and tailwinds
            
            IMPORTANT: Your output MUST strictly follow the schema.
            """,
            agent=self.researcher_agent,
            expected_output=f"News summary and sentiment analysis for {ticker}.",
            output_pydantic=ResearcherOutput,
            async_execution=True,
        )

        # =========================================================
        # TASK 3: Report Generation (Reporter Agent)
        # Uses ReportOutput Pydantic schema for validation
        # =========================================================
        reporter_task = Task(
            description=f"""
            Create a professional equity research report for {ticker} using the 
            analysis from the Analyst and the news research from the Researcher.
            
            You will receive structured data from both agents. Use ONLY this data.
            
            Generate a comprehensive markdown report with these sections:
            1. Header: Ticker, date, sector, 5-tier rating, final score
            2. Executive Summary: Investment thesis + 5-7 bullet points
            3. Company Overview: Name, exchange, industry, market cap
            4. Recent Developments: News headlines and sentiment
            5. Financial Analysis: Valuation, profitability, growth, health
            6. Technical Analysis: Trend, RSI, drawdown
            7. Score Breakdown: All factor scores with interpretations
            8. Recommendation Rationale: 
               - Write 3-4 substantial paragraphs explaining the investment thesis
               - Paragraph 1: Summary of why the rating was assigned (connect final score to rating)
               - Paragraph 2: Key fundamental strengths/weaknesses driving the recommendation
               - Paragraph 3: Technical factors and market sentiment considerations
               - Paragraph 4: How this stock compares to sector benchmarks and peers
               - Support each point with specific data from the Analyst output
               
            9. Risks (provide 5-7 detailed risk factors):
               - List each risk as a bullet point with 2-3 sentences of explanation
               - Include quantitative context where available (e.g., "Debt-to-equity of X is above sector median of Y")
               - Cover: Financial risks, operational risks, market/sector risks, valuation risks
               - Incorporate any negative news sentiment from the Researcher output
               - Rate each risk as HIGH/MEDIUM/LOW impact
               
            10. Opportunities (provide 5-7 detailed catalysts):
               - List each opportunity as a bullet point with 2-3 sentences of explanation
               - Include specific metrics that support the opportunity
               - Cover: Growth catalysts, margin expansion potential, market tailwinds, competitive advantages
               - Incorporate any positive news/developments from the Researcher output
               - Estimate timeframe where possible (near-term, medium-term, long-term)
               
            11. Conclusion:
               - Write 2-3 paragraphs summarizing the investment case
               - Paragraph 1: Restate the recommendation with conviction level and target audience (growth investors, value investors, etc.)
               - Paragraph 2: Summarize the risk/reward balance and key metrics to monitor
               - Paragraph 3: Provide specific guidance on position sizing consideration based on risk level
               - End with a clear, actionable statement
            
            Rating scale (based on final_score):
            - 80-100: STRONG BUY
            - 65-79: BUY
            - 45-64: HOLD
            - 30-44: REDUCE
            - 0-29: SELL
            
            Confidence level:
            - HIGH: Complete data, strong conviction
            - MEDIUM: Some data gaps or mixed signals
            - LOW: Significant data gaps or high uncertainty
            
            Risk level:
            - HIGH: Max drawdown > 35% or weak financial health
            - MEDIUM: Max drawdown 20-35% or moderate concerns
            - LOW: Max drawdown < 20% and strong fundamentals
            
            CRITICAL OUTPUT INSTRUCTIONS:
            1. Target Price: Use the 'market_consensus' data from the Analyst output to fill the 'target_price' field.
            2. Score Interpretations: You MUST populate the 'score_interpretations' list. 
               For EVERY score in the Analyst's 'scores' section (Valuation, Growth, Profitability, Health, Technical),
               create an entry with the score value and a 1-sentence human-readable interpretation.
               DO NOT leave this list empty.
            CRITICAL: Do NOT invent any data. Use only what Analyst and Researcher provided.
            If something is missing, write "Not available".
            """,
            agent=self.reporter_agent,
            expected_output=f"Professional equity research report for {ticker}.",
            output_pydantic=ReportOutput,  # Enforce Pydantic schema
            context=[analyst_task, researcher_task],
            async_execution=False,
        )

        # =========================================================
        # CREATE AND RUN THE CREW
        # =========================================================
        crew = Crew(
            agents=[
                self.analyst_agent,
                self.researcher_agent,
                self.reporter_agent,
            ],
            tasks=[
                analyst_task,
                researcher_task,
                reporter_task,
            ],
            process=Process.sequential,
            verbose=True,
        )

        # Execute the crew
        result = crew.kickoff()

        # =========================================================
        # COLLECT AND STRUCTURE ALL OUTPUTS
        # =========================================================
        output = self._collect_outputs(
            result=result,
            analyst_task=analyst_task,
            researcher_task=researcher_task,
            reporter_task=reporter_task,
            ticker=ticker,
            sector=sector,
        )

        return output

    def _collect_outputs(
        self,
        result,
        analyst_task: Task,
        researcher_task: Task,
        reporter_task: Task,
        ticker: str,
        sector: str,
    ) -> Dict[str, Any]:
        """
        Collect and structure outputs from all tasks.

        With Pydantic schemas, task outputs are already validated objects.
        We convert them to dicts for JSON serialization.
        """
        output = {
            "ticker": ticker,
            "sector": sector,
            "as_of_date": date.today().isoformat(),
        }

        # =========================================================
        # Extract Reporter output (final result)
        # =========================================================
        try:
            if hasattr(result, "pydantic") and result.pydantic:
                # Pydantic object returned directly
                report_data = result.pydantic.model_dump()
            elif hasattr(result, "raw"):
                # Fallback to raw parsing with safe parser
                report_data = safe_json_parse(result.raw, {})
            else:
                report_data = safe_json_parse(str(result), {})

            output.update(report_data)
        except Exception as e:
            output["report_parse_error"] = str(e)
            output["report_markdown"] = str(
                result.raw if hasattr(result, "raw") else result
            )

        # =========================================================
        # Extract Analyst output
        # =========================================================
        try:
            if hasattr(analyst_task, "output") and analyst_task.output:
                if (
                    hasattr(analyst_task.output, "pydantic")
                    and analyst_task.output.pydantic
                ):
                    analyst_data = analyst_task.output.pydantic.model_dump()
                elif hasattr(analyst_task.output, "raw"):
                    analyst_data = safe_json_parse(analyst_task.output.raw, {})
                else:
                    analyst_data = safe_json_parse(str(analyst_task.output), {})

                output["analyst"] = analyst_data

                # Extract key fields to top level
                if "scores" in analyst_data:
                    output["scores"] = analyst_data["scores"]
                if "technical_indicators" in analyst_data:
                    output["technical_indicators"] = analyst_data[
                        "technical_indicators"
                    ]
                if "fundamental_metrics" in analyst_data:
                    output["fundamental_metrics"] = analyst_data["fundamental_metrics"]
                if "company_profile" in analyst_data:
                    output["company_profile"] = analyst_data["company_profile"]
                if "sector_benchmarks" in analyst_data:
                    output["sector_benchmarks"] = analyst_data["sector_benchmarks"]
                if "analyst_summary" in analyst_data:
                    output["analyst_summary"] = analyst_data["analyst_summary"]
        except Exception as e:
            output["analyst_parse_error"] = str(e)

        # =========================================================
        # Extract Researcher output
        # =========================================================
        try:
            if hasattr(researcher_task, "output") and researcher_task.output:
                if (
                    hasattr(researcher_task.output, "pydantic")
                    and researcher_task.output.pydantic
                ):
                    researcher_data = researcher_task.output.pydantic.model_dump()
                elif hasattr(researcher_task.output, "raw"):
                    researcher_data = safe_json_parse(researcher_task.output.raw, {})
                else:
                    researcher_data = safe_json_parse(str(researcher_task.output), {})

                output["researcher"] = researcher_data

                # Extract key fields to top level
                if "headline_summary" in researcher_data:
                    output["headline_summary"] = researcher_data["headline_summary"]
                if "sentiment" in researcher_data:
                    output["sentiment"] = researcher_data["sentiment"]
                if "key_risks" in researcher_data:
                    output["key_risks"] = researcher_data["key_risks"]
                if "key_tailwinds" in researcher_data:
                    output["key_tailwinds"] = researcher_data["key_tailwinds"]
                if "news_source" in researcher_data:
                    output["news_source"] = researcher_data["news_source"]
        except Exception as e:
            output["researcher_parse_error"] = str(e)

        return output

    def run_analysis_only(
        self,
        ticker: str,
        sector: str,
    ) -> Dict[str, Any]:
        """
        Run only the analysis phase (Analyst + Researcher) without report generation.

        Args:
            ticker: Stock ticker symbol
            sector: Sector for benchmarks

        Returns:
            Dict with analyst and researcher outputs.
        """
        analyst_task = Task(
            description=f"Analyze {ticker} in {sector} sector using your quantitative tools.",
            agent=self.analyst_agent,
            expected_output="Structured analysis with scores and metrics.",
            output_pydantic=AnalystOutput,
            async_execution=True,
        )

        researcher_task = Task(
            description=f"Research recent news for {ticker} using search tools.",
            agent=self.researcher_agent,
            expected_output="News summary with sentiment analysis.",
            output_pydantic=ResearcherOutput,
            async_execution=True,
        )

        # Aggregation task
        aggregation_task = Task(
            description="""
            Combine the analyst and researcher outputs into a single response.
            Simply acknowledge that you have received both outputs.
            """,
            agent=self.reporter_agent,
            expected_output="Confirmation of received data.",
            context=[analyst_task, researcher_task],
            async_execution=False,
        )

        crew = Crew(
            agents=[self.analyst_agent, self.researcher_agent, self.reporter_agent],
            tasks=[analyst_task, researcher_task, aggregation_task],
            process=Process.sequential,
            verbose=True,
        )

        result = crew.kickoff()

        # Collect outputs
        output = {
            "ticker": ticker,
            "sector": sector,
        }

        try:
            if hasattr(analyst_task, "output") and analyst_task.output:
                if (
                    hasattr(analyst_task.output, "pydantic")
                    and analyst_task.output.pydantic
                ):
                    output["analyst"] = analyst_task.output.pydantic.model_dump()
                elif hasattr(analyst_task.output, "raw"):
                    output["analyst"] = safe_json_parse(analyst_task.output.raw, {})
        except Exception as e:
            output["analyst_error"] = str(e)

        try:
            if hasattr(researcher_task, "output") and researcher_task.output:
                if (
                    hasattr(researcher_task.output, "pydantic")
                    and researcher_task.output.pydantic
                ):
                    output["researcher"] = researcher_task.output.pydantic.model_dump()
                elif hasattr(researcher_task.output, "raw"):
                    output["researcher"] = safe_json_parse(
                        researcher_task.output.raw, {}
                    )
        except Exception as e:
            output["researcher_error"] = str(e)

        return output
