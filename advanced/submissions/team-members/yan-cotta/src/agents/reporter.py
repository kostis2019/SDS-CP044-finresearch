"""
Reporter Agent - Investment report synthesis specialist.

The Reporter agent combines qualitative and quantitative findings
into a professional, structured investment research report.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from crewai import Agent
from pydantic import BaseModel, Field

from src.agents.base import BaseAgentFactory, create_llm
from src.config.settings import get_settings
from src.tools.memory import MemoryTool


logger = logging.getLogger(__name__)


# =============================================================================
# Pydantic Models for Report Structure
# =============================================================================

class ReportSection(BaseModel):
    """A single section of the research report."""
    title: str = Field(..., description="Section heading")
    content: str = Field(..., description="Section content in markdown")


class ReportOutput(BaseModel):
    """
    Structured output from the Reporter agent.
    
    This model ensures the report contains all required sections
    and provides validation for quality control.
    """
    ticker: str = Field(..., description="Stock ticker symbol")
    company_name: str = Field(..., description="Full company name")
    generated_at: datetime = Field(default_factory=datetime.now)
    
    executive_summary: str = Field(..., description="High-level investment thesis")
    company_overview: str = Field(default="", description="Brief company description")
    market_data: str = Field(..., description="Quantitative metrics and price data")
    news_analysis: str = Field(..., description="Recent news and developments")
    risk_assessment: str = Field(..., description="Key risks and concerns")
    investment_considerations: str = Field(default="", description="Bull/bear case")
    disclaimer: str = Field(
        default=(
            "This report is for informational purposes only and does not "
            "constitute investment advice. Past performance is not indicative "
            "of future results. Always conduct your own research and consult "
            "with a qualified financial advisor before making investment decisions."
        ),
        description="Legal disclaimer"
    )
    
    def to_markdown(self) -> str:
        """
        Convert the report to a formatted Markdown string.
        
        Returns:
            Complete markdown report with all sections
        """
        lines = [
            f"# Investment Research Report: {self.company_name} ({self.ticker})",
            "",
            f"**Generated:** {self.generated_at.strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "---",
            "",
            "## Executive Summary",
            "",
            self.executive_summary,
            "",
        ]
        
        if self.company_overview:
            lines.extend([
                "## Company Overview",
                "",
                self.company_overview,
                "",
            ])
        
        lines.extend([
            "## Market Data & Financial Metrics",
            "",
            self.market_data,
            "",
            "## News Analysis & Recent Developments",
            "",
            self.news_analysis,
            "",
            "## Risk Assessment",
            "",
            self.risk_assessment,
            "",
        ])
        
        if self.investment_considerations:
            lines.extend([
                "## Investment Considerations",
                "",
                self.investment_considerations,
                "",
            ])
        
        lines.extend([
            "---",
            "",
            "## Disclaimer",
            "",
            f"*{self.disclaimer}*",
            "",
        ])
        
        return "\n".join(lines)
    
    def validate_quality(self) -> tuple[bool, List[str]]:
        """
        Validate report meets quality standards.
        
        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []
        
        # Minimum content length checks
        if len(self.executive_summary) < 100:
            issues.append("Executive summary is too short (min 100 chars)")
        
        if len(self.market_data) < 50:
            issues.append("Market data section is too short (min 50 chars)")
        
        if len(self.news_analysis) < 50:
            issues.append("News analysis section is too short (min 50 chars)")
        
        if len(self.risk_assessment) < 50:
            issues.append("Risk assessment section is too short (min 50 chars)")
        
        return (len(issues) == 0, issues)


class ReportBuilder:
    """
    Builder class for constructing reports from memory findings.
    
    Retrieves stored findings from ChromaDB and structures them
    into a professional research report.
    """
    
    def __init__(self, memory_tool: MemoryTool, ticker: str, company_name: str):
        """
        Initialize the report builder.
        
        Args:
            memory_tool: Memory tool for retrieving findings
            ticker: Stock ticker symbol
            company_name: Company name for the report
        """
        self.memory_tool = memory_tool
        self.ticker = ticker
        self.company_name = company_name
        self._findings: dict[str, List[str]] = {}
    
    def retrieve_findings(self) -> dict[str, List[str]]:
        """
        Retrieve all findings from memory categorized by type.
        
        Returns:
            Dictionary mapping category to list of findings
        """
        logger.info(f"Retrieving findings from memory for {self.ticker}")
        
        categories = {
            "news": f"{self.ticker} news developments announcements",
            "metrics": f"{self.ticker} financial metrics valuation price",
            "analysis": f"{self.ticker} analysis assessment risk sentiment",
            "general": f"{self.ticker} research findings",
        }
        
        for category, query in categories.items():
            findings = self.memory_tool.get_context(query)
            self._findings[category] = findings
            logger.debug(f"Retrieved {len(findings)} findings for category: {category}")
        
        return self._findings
    
    def build_section(self, category: str, fallback: str = "") -> str:
        """
        Build a section from memory findings.
        
        Args:
            category: Category of findings to use
            fallback: Fallback text if no findings exist
            
        Returns:
            Formatted section content
        """
        findings = self._findings.get(category, [])
        
        if not findings:
            logger.warning(f"No findings found for category: {category}")
            return fallback or f"*No {category} data available at this time.*"
        
        # Format findings as bullet points
        lines = []
        for i, finding in enumerate(findings, 1):
            # Clean up the finding text
            text = finding.strip()
            if text:
                lines.append(f"- {text}")
        
        return "\n".join(lines) if lines else fallback
    
    def build_report(self) -> ReportOutput:
        """
        Build the complete report from retrieved findings.
        
        Returns:
            Structured ReportOutput object
        """
        if not self._findings:
            self.retrieve_findings()
        
        # Combine findings into sections
        news_content = self.build_section(
            "news",
            fallback="*No recent news available.*"
        )
        
        metrics_content = self.build_section(
            "metrics",
            fallback="*Financial metrics pending retrieval.*"
        )
        
        analysis_content = self.build_section(
            "analysis",
            fallback="*Risk analysis pending.*"
        )
        
        # Build executive summary from all findings
        all_findings = []
        for findings in self._findings.values():
            all_findings.extend(findings)
        
        summary_text = (
            f"This report presents a comprehensive analysis of {self.company_name} "
            f"({self.ticker}), incorporating both qualitative research and "
            f"quantitative financial data. "
        )
        
        if all_findings:
            summary_text += "Key findings include: " + "; ".join(
                f[:100] for f in all_findings[:3] if f
            )
        
        return ReportOutput(
            ticker=self.ticker,
            company_name=self.company_name,
            executive_summary=summary_text,
            market_data=metrics_content,
            news_analysis=news_content,
            risk_assessment=analysis_content,
        )


class ReporterAgent:
    """
    Factory and wrapper for the Reporter Agent.
    
    The Reporter agent:
    - Retrieves findings from team memory
    - Synthesizes research and analysis into coherent narrative
    - Structures reports in professional format
    - Includes appropriate disclaimers and caveats
    """
    
    AGENT_NAME = "reporter"
    
    def __init__(self, memory_tool: Optional[MemoryTool] = None):
        """
        Initialize the Reporter agent factory.
        
        Args:
            memory_tool: Optional shared memory tool instance
        """
        self._memory_tool = memory_tool or MemoryTool()
        self._agent: Optional[Agent] = None
        self._report_builder: Optional[ReportBuilder] = None
    
    def create(self) -> Agent:
        """
        Create and return the Reporter agent.
        
        Returns:
            Configured Reporter Agent instance
        """
        if self._agent is not None:
            return self._agent
        
        settings = get_settings()
        
        # Reporter uses balanced temperature for structured writing
        llm = create_llm(
            model=settings.worker_model,
            temperature=settings.reporter_temperature
        )
        
        # Reporter only needs memory tool to access team findings
        tools = [self._memory_tool]
        
        self._agent = BaseAgentFactory.create_agent(
            agent_name=self.AGENT_NAME,
            llm=llm,
            tools=tools
        )
        
        logger.info("Reporter agent created successfully")
        return self._agent
    
    @property
    def agent(self) -> Agent:
        """Get the agent instance, creating if necessary."""
        if self._agent is None:
            self.create()
        return self._agent
    
    def get_report_builder(self, ticker: str, company_name: str) -> ReportBuilder:
        """
        Get or create a report builder for the given ticker.
        
        Args:
            ticker: Stock ticker symbol
            company_name: Company name
            
        Returns:
            ReportBuilder instance
        """
        if (
            self._report_builder is None
            or self._report_builder.ticker != ticker
        ):
            self._report_builder = ReportBuilder(
                memory_tool=self._memory_tool,
                ticker=ticker,
                company_name=company_name
            )
        return self._report_builder
    
    def generate_structured_report(
        self,
        ticker: str,
        company_name: str
    ) -> ReportOutput:
        """
        Generate a structured report from memory findings.
        
        This method bypasses the LLM and directly builds a report
        from stored findings. Useful for testing and validation.
        
        Args:
            ticker: Stock ticker symbol
            company_name: Company name
            
        Returns:
            Structured ReportOutput object
        """
        logger.info(f"Generating structured report for {ticker}")
        builder = self.get_report_builder(ticker, company_name)
        return builder.build_report()
    
    def save_report_to_file(
        self,
        report: ReportOutput,
        output_dir: Path
    ) -> Path:
        """
        Save a report to a markdown file.
        
        Args:
            report: ReportOutput to save
            output_dir: Directory to save the report
            
        Returns:
            Path to the saved file
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        
        filename = f"{report.ticker}_report.md"
        filepath = output_dir / filename
        
        content = report.to_markdown()
        filepath.write_text(content)
        
        logger.info(f"Report saved to {filepath}")
        return filepath
