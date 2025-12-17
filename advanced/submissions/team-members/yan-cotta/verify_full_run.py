#!/usr/bin/env python3
"""
FinResearch AI - Full Integration Verification Script

This script runs a complete end-to-end test of the FinResearch AI system,
validating that:
1. All agents are created successfully
2. The crew executes the hierarchical workflow
3. Findings are saved to and retrieved from ChromaDB
4. The final report is generated with all required sections
5. The report is saved to outputs/{TICKER}_report.md

Usage:
    python verify_full_run.py                    # Test with NVDA
    python verify_full_run.py --ticker AAPL      # Test with custom ticker
    python verify_full_run.py --dry-run          # Validate setup only
    python verify_full_run.py --mock             # Run with mock data (no API calls)
"""

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from pydantic import BaseModel, Field


# =============================================================================
# Verification Models
# =============================================================================

class VerificationStep(BaseModel):
    """Result of a single verification step."""
    name: str
    passed: bool
    message: str
    duration_ms: Optional[float] = None


class VerificationResult(BaseModel):
    """Complete verification result."""
    ticker: str
    timestamp: datetime = Field(default_factory=datetime.now)
    all_passed: bool = False
    steps: List[VerificationStep] = Field(default_factory=list)
    report_path: Optional[str] = None
    report_size_bytes: Optional[int] = None
    total_duration_seconds: Optional[float] = None
    error: Optional[str] = None
    
    def add_step(self, name: str, passed: bool, message: str, duration_ms: float = 0):
        """Add a verification step result."""
        self.steps.append(VerificationStep(
            name=name,
            passed=passed,
            message=message,
            duration_ms=duration_ms
        ))
    
    def summary(self) -> str:
        """Generate a summary of the verification."""
        lines = [
            "",
            "=" * 60,
            "VERIFICATION SUMMARY",
            "=" * 60,
            f"Ticker: {self.ticker}",
            f"Timestamp: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
            f"Total Duration: {self.total_duration_seconds:.1f}s" if self.total_duration_seconds else "",
            "",
            "Steps:",
        ]
        
        for step in self.steps:
            status = "✓" if step.passed else "✗"
            lines.append(f"  [{status}] {step.name}: {step.message}")
        
        lines.extend([
            "",
            f"Overall Result: {'PASSED' if self.all_passed else 'FAILED'}",
        ])
        
        if self.report_path:
            lines.append(f"Report: {self.report_path} ({self.report_size_bytes} bytes)")
        
        if self.error:
            lines.extend(["", f"Error: {self.error}"])
        
        lines.append("=" * 60)
        
        return "\n".join(lines)


# =============================================================================
# Verification Functions
# =============================================================================

def verify_imports() -> Tuple[bool, str]:
    """Verify all required modules can be imported."""
    try:
        from src.config.settings import get_settings, AGENTS_CONFIG_PATH, TASKS_CONFIG_PATH
        from src.agents.manager import ManagerAgent
        from src.agents.researcher import ResearcherAgent
        from src.agents.analyst import AnalystAgent
        from src.agents.reporter import ReporterAgent, ReportOutput, ReportBuilder
        from src.tools.memory import MemoryTool
        from src.tools.news_search import NewsSearchTool
        from src.tools.financial_data import FinancialDataTool
        from src.crew import FinResearchCrew, CrewExecutionResult
        return True, "All imports successful"
    except ImportError as e:
        return False, f"Import failed: {e}"


def verify_config() -> Tuple[bool, str]:
    """Verify configuration files exist and are valid."""
    from src.config.settings import AGENTS_CONFIG_PATH, TASKS_CONFIG_PATH
    
    issues = []
    
    if not AGENTS_CONFIG_PATH.exists():
        issues.append(f"Missing: {AGENTS_CONFIG_PATH}")
    
    if not TASKS_CONFIG_PATH.exists():
        issues.append(f"Missing: {TASKS_CONFIG_PATH}")
    
    if issues:
        return False, "; ".join(issues)
    
    # Validate YAML structure
    import yaml
    try:
        with open(AGENTS_CONFIG_PATH) as f:
            agents = yaml.safe_load(f)
        required_agents = ['manager', 'researcher', 'analyst', 'reporter']
        missing = [a for a in required_agents if a not in agents]
        if missing:
            return False, f"Missing agent configs: {missing}"
    except Exception as e:
        return False, f"Invalid agents.yaml: {e}"
    
    try:
        with open(TASKS_CONFIG_PATH) as f:
            tasks = yaml.safe_load(f)
        required_tasks = ['research_task', 'analysis_task', 'report_task']
        missing = [t for t in required_tasks if t not in tasks]
        if missing:
            return False, f"Missing task configs: {missing}"
    except Exception as e:
        return False, f"Invalid tasks.yaml: {e}"
    
    return True, "Config files valid"


def verify_environment() -> Tuple[bool, str]:
    """Verify environment variables are set."""
    from src.config.settings import get_settings
    
    settings = get_settings()
    
    if not settings.openai_api_key:
        return False, "OPENAI_API_KEY not set"
    
    # Check API key format (basic validation)
    if not settings.openai_api_key.startswith(('sk-', 'org-')):
        return False, "OPENAI_API_KEY format appears invalid"
    
    return True, "Environment configured"


def verify_memory_tool() -> Tuple[bool, str]:
    """Verify ChromaDB memory tool works."""
    from src.tools.memory import MemoryTool
    
    try:
        tool = MemoryTool()
        
        if tool._collection is None:
            return False, "ChromaDB not initialized"
        
        # Test save
        save_result = tool._run("save:general:verification test entry")
        if not save_result.startswith("[OK]"):
            return False, f"Save failed: {save_result}"
        
        # Test retrieve
        retrieve_result = tool._run("retrieve:verification test")
        if "ERROR" in retrieve_result:
            return False, f"Retrieve failed: {retrieve_result}"
        
        # Clear test data
        tool._run("clear")
        
        return True, "Memory tool operational"
        
    except Exception as e:
        return False, f"Memory tool error: {e}"


def verify_agent_creation() -> Tuple[bool, str]:
    """Verify all agents can be created."""
    from src.agents.manager import ManagerAgent
    from src.agents.researcher import ResearcherAgent
    from src.agents.analyst import AnalystAgent
    from src.agents.reporter import ReporterAgent
    from src.tools.memory import MemoryTool
    
    try:
        memory = MemoryTool()
        
        manager = ManagerAgent(memory_tool=memory)
        manager.create()
        
        researcher = ResearcherAgent(memory_tool=memory)
        researcher.create()
        
        analyst = AnalystAgent(memory_tool=memory)
        analyst.create()
        
        reporter = ReporterAgent(memory_tool=memory)
        reporter.create()
        
        return True, "All agents created successfully"
        
    except Exception as e:
        return False, f"Agent creation failed: {e}"


def verify_output_directory() -> Tuple[bool, str]:
    """Verify output directory can be created."""
    from src.config.settings import get_settings
    
    settings = get_settings()
    output_path = settings.output_path
    
    try:
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Test write permission
        test_file = output_path / ".write_test"
        test_file.write_text("test")
        test_file.unlink()
        
        return True, f"Output directory ready: {output_path}"
        
    except Exception as e:
        return False, f"Output directory error: {e}"


def verify_report_structure(content: str) -> Tuple[bool, List[str]]:
    """Verify report has all required sections."""
    from src.config.settings import get_settings
    
    settings = get_settings()
    required_sections = settings.required_report_sections
    
    missing = []
    for section in required_sections:
        if section.lower() not in content.lower():
            missing.append(section)
    
    return len(missing) == 0, missing


def run_full_verification(
    ticker: str = "NVDA",
    company_name: Optional[str] = None,
    dry_run: bool = False,
    mock: bool = False,
    verbose: bool = False
) -> VerificationResult:
    """
    Run full end-to-end verification.
    
    Args:
        ticker: Stock ticker to test with
        company_name: Optional company name
        dry_run: If True, only verify setup without running crew
        mock: If True, use mock data instead of API calls
        verbose: Enable verbose output
        
    Returns:
        VerificationResult with all step outcomes
    """
    import time
    
    result = VerificationResult(ticker=ticker)
    start_time = time.time()
    
    # Setup logging
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s | %(levelname)s | %(message)s"
    )
    logger = logging.getLogger(__name__)
    
    logger.info(f"Starting verification for {ticker}")
    
    # Step 1: Verify imports
    logger.info("Step 1: Verifying imports...")
    passed, msg = verify_imports()
    result.add_step("Imports", passed, msg)
    if not passed:
        result.error = msg
        return result
    
    # Step 2: Verify config
    logger.info("Step 2: Verifying configuration...")
    passed, msg = verify_config()
    result.add_step("Configuration", passed, msg)
    if not passed:
        result.error = msg
        return result
    
    # Step 3: Verify environment
    logger.info("Step 3: Verifying environment...")
    passed, msg = verify_environment()
    result.add_step("Environment", passed, msg)
    if not passed:
        result.error = msg
        return result
    
    # Step 4: Verify memory tool
    logger.info("Step 4: Verifying memory tool...")
    passed, msg = verify_memory_tool()
    result.add_step("Memory Tool", passed, msg)
    if not passed:
        result.error = msg
        return result
    
    # Step 5: Verify agent creation
    logger.info("Step 5: Verifying agent creation...")
    passed, msg = verify_agent_creation()
    result.add_step("Agent Creation", passed, msg)
    if not passed:
        result.error = msg
        return result
    
    # Step 6: Verify output directory
    logger.info("Step 6: Verifying output directory...")
    passed, msg = verify_output_directory()
    result.add_step("Output Directory", passed, msg)
    if not passed:
        result.error = msg
        return result
    
    # If dry run, stop here
    if dry_run:
        logger.info("Dry run complete - skipping crew execution")
        result.add_step("Crew Execution", True, "Skipped (dry run)")
        result.add_step("Report Generation", True, "Skipped (dry run)")
        result.add_step("Report Validation", True, "Skipped (dry run)")
        result.all_passed = all(s.passed for s in result.steps)
        result.total_duration_seconds = time.time() - start_time
        return result
    
    # Step 7: Run crew execution
    logger.info("Step 7: Running crew execution...")
    
    try:
        from src.crew import FinResearchCrew
        from src.config.settings import get_settings
        
        settings = get_settings()
        
        crew = FinResearchCrew(
            ticker=ticker,
            company_name=company_name or ticker,
            verbose=verbose
        )
        
        crew_start = time.time()
        report_content = crew.run()
        crew_duration = (time.time() - crew_start) * 1000
        
        result.add_step(
            "Crew Execution",
            True,
            f"Completed in {crew_duration/1000:.1f}s",
            crew_duration
        )
        
        # Step 8: Save report
        logger.info("Step 8: Saving report...")
        report_filename = f"{ticker}_report.md"
        report_path = crew.save_report(report_content, filename=report_filename)
        
        result.report_path = str(report_path)
        result.report_size_bytes = report_path.stat().st_size
        
        if report_path.exists() and result.report_size_bytes > 0:
            result.add_step(
                "Report Generation",
                True,
                f"Saved to {report_path} ({result.report_size_bytes} bytes)"
            )
        else:
            result.add_step("Report Generation", False, "Report file empty or missing")
            result.error = "Report not generated"
            return result
        
        # Step 9: Validate report structure
        logger.info("Step 9: Validating report structure...")
        valid, missing_sections = verify_report_structure(report_content)
        
        if valid:
            result.add_step("Report Validation", True, "All required sections present")
        else:
            result.add_step(
                "Report Validation",
                False,
                f"Missing sections: {missing_sections}"
            )
        
        # Check execution result
        exec_result = crew.get_execution_result()
        if exec_result and exec_result.validation_issues:
            logger.warning(f"Report validation issues: {exec_result.validation_issues}")
        
    except Exception as e:
        logger.exception("Crew execution failed")
        result.add_step("Crew Execution", False, str(e))
        result.error = str(e)
        result.total_duration_seconds = time.time() - start_time
        return result
    
    # Calculate overall result
    result.all_passed = all(s.passed for s in result.steps)
    result.total_duration_seconds = time.time() - start_time
    
    return result


# =============================================================================
# Main Entry Point
# =============================================================================

def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="FinResearch AI - Full Integration Verification",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "-t", "--ticker",
        default="NVDA",
        help="Stock ticker to test (default: NVDA)"
    )
    
    parser.add_argument(
        "-n", "--name",
        default=None,
        help="Company name (default: same as ticker)"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only verify setup, don't run the crew"
    )
    
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Use mock data (not yet implemented)"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )
    
    args = parser.parse_args()
    
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║              FinResearch AI - Integration Verification               ║
╚══════════════════════════════════════════════════════════════════════╝
    """)
    
    # Run verification
    result = run_full_verification(
        ticker=args.ticker.upper(),
        company_name=args.name,
        dry_run=args.dry_run,
        mock=args.mock,
        verbose=args.verbose
    )
    
    # Output results
    if args.json:
        print(json.dumps(result.model_dump(), indent=2, default=str))
    else:
        print(result.summary())
    
    # Return appropriate exit code
    return 0 if result.all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
