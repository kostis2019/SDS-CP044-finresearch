"""
FinResearch Crew - Hierarchical multi-agent orchestration.

This module provides the main crew assembly and execution logic,
coordinating the Manager, Researcher, Analyst, and Reporter agents.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from crewai import Crew, Task, Process
from pydantic import BaseModel, Field

from src.agents.manager import ManagerAgent
from src.agents.researcher import ResearcherAgent
from src.agents.analyst import AnalystAgent
from src.agents.reporter import ReporterAgent, ReportOutput
from src.config.settings import get_settings, TASKS_CONFIG_PATH
from src.tools.memory import MemoryTool
from src.tools.news_search import NewsSearchTool
from src.tools.financial_data import FinancialDataTool


logger = logging.getLogger(__name__)


# =============================================================================
# Pydantic Models for Research Output
# =============================================================================

class ResearchResult(BaseModel):
    """Result from the research phase."""
    ticker: str = Field(..., description="Stock ticker symbol")
    company_name: str = Field(..., description="Company name")
    news_summary: str = Field(default="", description="Summary of recent news")
    sentiment: str = Field(default="neutral", description="Market sentiment")
    key_developments: List[str] = Field(default_factory=list)
    risk_factors: List[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.now)


class AnalysisResult(BaseModel):
    """Result from the analysis phase."""
    ticker: str = Field(..., description="Stock ticker symbol")
    current_price: Optional[float] = Field(default=None)
    price_change_pct: Optional[float] = Field(default=None)
    pe_ratio: Optional[float] = Field(default=None)
    market_cap: Optional[str] = Field(default=None)
    metrics_summary: str = Field(default="", description="Summary of metrics")
    timestamp: datetime = Field(default_factory=datetime.now)


class CrewExecutionResult(BaseModel):
    """
    Complete result from crew execution.
    
    This model provides a clean interface for UI consumption.
    """
    ticker: str = Field(..., description="Stock ticker symbol")
    company_name: str = Field(..., description="Company name")
    
    # Execution metadata
    started_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = Field(default=None)
    duration_seconds: Optional[float] = Field(default=None)
    status: str = Field(default="pending", description="pending|running|completed|failed")
    error_message: Optional[str] = Field(default=None)
    
    # Output artifacts
    raw_output: str = Field(default="", description="Raw crew output")
    report_content: str = Field(default="", description="Formatted markdown report")
    report_path: Optional[str] = Field(default=None, description="Path to saved report")
    
    # Quality metrics
    report_valid: bool = Field(default=False)
    validation_issues: List[str] = Field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return self.model_dump()


def load_tasks_config() -> Dict[str, Any]:
    """
    Load task configurations from YAML file.
    
    Returns:
        Dictionary with task configurations
    """
    if not TASKS_CONFIG_PATH.exists():
        raise FileNotFoundError(f"Tasks config not found: {TASKS_CONFIG_PATH}")
    
    with open(TASKS_CONFIG_PATH, 'r') as f:
        config = yaml.safe_load(f)
    
    logger.debug(f"Loaded tasks config from {TASKS_CONFIG_PATH}")
    return config


class FinResearchCrew:
    """
    Main crew orchestrator for financial research.
    
    Coordinates a hierarchical multi-agent workflow:
    1. Manager receives the research request
    2. Manager delegates to Researcher (qualitative) and Analyst (quantitative)
    3. Workers save findings to shared memory
    4. Reporter synthesizes findings into final report
    
    Attributes:
        ticker: Stock ticker symbol being researched
        company_name: Full company name (optional, for context)
    """
    
    def __init__(
        self,
        ticker: str,
        company_name: Optional[str] = None,
        verbose: bool = True
    ):
        """
        Initialize the research crew.
        
        Args:
            ticker: Stock ticker symbol to research
            company_name: Optional company name for context
            verbose: Whether to enable verbose logging
        """
        self.ticker = ticker.strip().upper()
        self.company_name = company_name or self.ticker
        self.verbose = verbose
        
        self._settings = get_settings()
        self._tasks_config = load_tasks_config()
        
        # Shared tools (single instances for all agents)
        self._memory_tool = MemoryTool()
        self._news_tool = NewsSearchTool()
        self._financial_tool = FinancialDataTool()
        
        # Agent factories
        self._manager_factory = ManagerAgent(memory_tool=self._memory_tool)
        self._researcher_factory = ResearcherAgent(
            memory_tool=self._memory_tool,
            news_tool=self._news_tool
        )
        self._analyst_factory = AnalystAgent(
            memory_tool=self._memory_tool,
            financial_tool=self._financial_tool
        )
        self._reporter_factory = ReporterAgent(memory_tool=self._memory_tool)
        
        # Crew instance (created on run)
        self._crew: Optional[Crew] = None
        
        # Execution result
        self._result: Optional[CrewExecutionResult] = None
        
        logger.info(f"FinResearchCrew initialized for {self.ticker}")
    
    def _format_task_description(self, template: str) -> str:
        """Format task template with ticker and company name."""
        return template.format(
            ticker=self.ticker,
            company_name=self.company_name
        )
    
    def _create_tasks(self) -> list[Task]:
        """
        Create all tasks for the research workflow.
        
        Research and Analysis tasks run in parallel (async_execution: true).
        Report task waits for both via context dependency.
        
        Returns:
            List of configured Task instances
        """
        # Get agents
        researcher = self._researcher_factory.create()
        analyst = self._analyst_factory.create()
        reporter = self._reporter_factory.create()
        
        # Research Task (runs async/parallel)
        research_config = self._tasks_config['research_task']
        async_research = research_config.get('async_execution', False)
        research_task = Task(
            description=self._format_task_description(research_config['description']),
            expected_output=research_config['expected_output'].strip(),
            agent=researcher,
            async_execution=async_research
        )
        
        # Analysis Task (runs async/parallel)
        analysis_config = self._tasks_config['analysis_task']
        async_analysis = analysis_config.get('async_execution', False)
        analysis_task = Task(
            description=self._format_task_description(analysis_config['description']),
            expected_output=analysis_config['expected_output'].strip(),
            agent=analyst,
            async_execution=async_analysis
        )
        
        # Report Task (waits for research and analysis via context)
        report_config = self._tasks_config['report_task']
        report_task = Task(
            description=self._format_task_description(report_config['description']),
            expected_output=report_config['expected_output'].strip(),
            agent=reporter,
            context=[research_task, analysis_task]  # Waits for both async tasks
        )
        
        parallel_mode = "parallel" if (async_research or async_analysis) else "sequential"
        logger.info(f"Created 3 tasks: research, analysis, report ({parallel_mode} mode)")
        return [research_task, analysis_task, report_task]
    
    def _create_crew(self) -> Crew:
        """
        Assemble the crew with all agents and tasks.
        
        Returns:
            Configured Crew instance
        """
        # Get all agents
        manager = self._manager_factory.create()
        researcher = self._researcher_factory.agent
        analyst = self._analyst_factory.agent
        reporter = self._reporter_factory.agent
        
        # Create tasks
        tasks = self._create_tasks()
        
        # Assemble crew with hierarchical process
        crew = Crew(
            agents=[researcher, analyst, reporter],
            tasks=tasks,
            manager_agent=manager,
            process=Process.hierarchical,
            verbose=self.verbose,
            memory=True,
            planning=True,  # Enable planning for better coordination
        )
        
        logger.info("Crew assembled with hierarchical process")
        return crew
    
    def _validate_report(self, content: str) -> tuple[bool, List[str]]:
        """
        Validate that the report meets quality standards.
        
        Args:
            content: Report content to validate
            
        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []
        settings = self._settings
        
        # Check minimum length
        if len(content) < 500:
            issues.append(f"Report too short: {len(content)} chars (min 500)")
        
        # Check for required sections
        for section in settings.required_report_sections:
            if section.lower() not in content.lower():
                issues.append(f"Missing required section: {section}")
        
        # Log validation results
        if issues:
            logger.warning(f"Report validation failed: {issues}")
        else:
            logger.info("Report passed quality validation")
        
        return (len(issues) == 0, issues)
    
    def run(self) -> str:
        """
        Execute the research workflow.
        
        Returns:
            Final research report as string
            
        Raises:
            Exception: If crew execution fails
        """
        logger.info(f"="*60)
        logger.info(f"STARTING RESEARCH: {self.ticker} ({self.company_name})")
        logger.info(f"="*60)
        
        # Initialize result tracking
        self._result = CrewExecutionResult(
            ticker=self.ticker,
            company_name=self.company_name,
            status="running"
        )
        
        # Clear previous memory for fresh research
        logger.info("Clearing previous memory context...")
        self._memory_tool._run("clear")
        
        # Create and run the crew
        self._crew = self._create_crew()
        
        try:
            logger.info("Kicking off crew execution...")
            result = self._crew.kickoff()
            
            raw_output = str(result)
            
            # Validate the output
            is_valid, issues = self._validate_report(raw_output)
            
            # Update result
            self._result.completed_at = datetime.now()
            self._result.duration_seconds = (
                self._result.completed_at - self._result.started_at
            ).total_seconds()
            self._result.status = "completed"
            self._result.raw_output = raw_output
            self._result.report_content = raw_output
            self._result.report_valid = is_valid
            self._result.validation_issues = issues
            
            logger.info(f"="*60)
            logger.info(f"RESEARCH COMPLETED: {self.ticker}")
            logger.info(f"Duration: {self._result.duration_seconds:.1f}s")
            logger.info(f"Report valid: {is_valid}")
            if issues:
                logger.warning(f"Validation issues: {issues}")
            logger.info(f"="*60)
            
            return raw_output
            
        except Exception as e:
            logger.exception(f"Crew execution failed for {self.ticker}")
            
            self._result.completed_at = datetime.now()
            self._result.status = "failed"
            self._result.error_message = str(e)
            
            raise
    
    def save_report(self, content: str, filename: Optional[str] = None) -> Path:
        """
        Save the research report to file.
        
        Args:
            content: Report content to save
            filename: Optional custom filename
            
        Returns:
            Path to saved report file
        """
        if filename is None:
            filename = f"{self.ticker}_report.md"
        
        output_path = self._settings.output_path / filename
        
        with open(output_path, 'w') as f:
            f.write(content)
        
        logger.info(f"Report saved to {output_path}")
        
        # Update result if tracking
        if self._result:
            self._result.report_path = str(output_path)
        
        return output_path
    
    def get_execution_result(self) -> Optional[CrewExecutionResult]:
        """
        Get the execution result for UI consumption.
        
        Returns:
            CrewExecutionResult if run() has been called, None otherwise
        """
        return self._result


class SequentialFinResearchCrew(FinResearchCrew):
    """
    Alternative crew using sequential process instead of hierarchical.
    
    Useful when:
    - Manager delegation isn't needed
    - Simpler, more predictable execution is preferred
    - Debugging individual agent behavior
    """
    
    def _create_crew(self) -> Crew:
        """Create crew with sequential process."""
        researcher = self._researcher_factory.create()
        analyst = self._analyst_factory.create()
        reporter = self._reporter_factory.create()
        
        tasks = self._create_tasks()
        
        crew = Crew(
            agents=[researcher, analyst, reporter],
            tasks=tasks,
            process=Process.sequential,
            verbose=self.verbose,
            memory=True,
        )
        
        logger.info("Crew assembled with sequential process")
        return crew
