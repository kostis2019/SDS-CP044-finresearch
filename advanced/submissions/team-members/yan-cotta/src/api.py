"""
FinResearch AI - FastAPI REST API Backend

This module provides a REST API wrapper around the CrewAI research workflow.
Supports asynchronous execution to prevent blocking the server during long-running
agent workflows.

Endpoints:
    POST /api/research - Execute research workflow for a stock ticker
    GET  /api/health   - Health check endpoint
    GET  /api/status/{task_id} - Check status of async research task
    
Production:
    Serves React frontend static assets when built
"""

import asyncio
import logging
import os
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field

# Add parent to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config.settings import get_settings, setup_logging
from src.crew import FinResearchCrew, SequentialFinResearchCrew, CrewExecutionResult
from src.tools.memory import MemoryTool


# =============================================================================
# Configuration
# =============================================================================

logger = logging.getLogger(__name__)

# Thread pool for running synchronous CrewAI in async context
executor = ThreadPoolExecutor(max_workers=3)

# In-memory task store (production would use Redis/DB)
task_store: Dict[str, "ResearchTask"] = {}


# =============================================================================
# Pydantic Models - API Schema
# =============================================================================

class ModelProvider(str, Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    GROQ = "groq"


class ResearchRequest(BaseModel):
    """Request body for POST /api/research."""
    ticker: str = Field(
        ...,
        min_length=1,
        max_length=10,
        description="Stock ticker symbol (e.g., AAPL, TSLA)",
        examples=["AAPL", "TSLA", "GOOGL"]
    )
    company_name: Optional[str] = Field(
        default=None,
        description="Optional company name for context"
    )
    reset_memory: bool = Field(
        default=False,
        description="Clear ChromaDB memory before starting"
    )
    model_provider: ModelProvider = Field(
        default=ModelProvider.OPENAI,
        description="LLM provider to use"
    )
    sequential_mode: bool = Field(
        default=True,
        description="Use sequential process (recommended for stability)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "ticker": "AAPL",
                "company_name": "Apple Inc",
                "reset_memory": False,
                "model_provider": "openai",
                "sequential_mode": True
            }
        }


class TaskStatus(str, Enum):
    """Status of an async research task."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class ResearchTask(BaseModel):
    """Model for tracking async research tasks."""
    task_id: str = Field(..., description="Unique task identifier")
    ticker: str = Field(..., description="Stock ticker being researched")
    status: TaskStatus = Field(default=TaskStatus.PENDING)
    created_at: datetime = Field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    progress_logs: List[str] = Field(default_factory=list)
    report: Optional[str] = None
    error_message: Optional[str] = None
    
    class Config:
        arbitrary_types_allowed = True


class ResearchResponse(BaseModel):
    """Response body for POST /api/research (sync mode)."""
    success: bool = Field(..., description="Whether research completed successfully")
    ticker: str = Field(..., description="Stock ticker researched")
    report: Optional[str] = Field(default=None, description="Markdown report content")
    logs: List[str] = Field(default_factory=list, description="Execution logs")
    duration_seconds: Optional[float] = Field(default=None)
    error: Optional[str] = Field(default=None, description="Error message if failed")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "ticker": "AAPL",
                "report": "# Financial Research Report: AAPL\n\n## Executive Summary...",
                "logs": ["Starting research...", "Research complete"],
                "duration_seconds": 45.2,
                "error": None
            }
        }


class AsyncResearchResponse(BaseModel):
    """Response for async research initiation."""
    task_id: str = Field(..., description="Task ID to poll for results")
    status: TaskStatus
    message: str


class HealthResponse(BaseModel):
    """Response for health check endpoint."""
    status: str = "healthy"
    version: str = "1.0.0"
    timestamp: datetime = Field(default_factory=datetime.now)


# =============================================================================
# FastAPI Application Setup
# =============================================================================

def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    
    Returns:
        Configured FastAPI instance
    """
    app = FastAPI(
        title="FinResearch AI API",
        description="""
        Multi-Agent Financial Research System API.
        
        This API provides endpoints to execute AI-powered financial research
        workflows using CrewAI agents.
        
        ## Features
        - Async research execution
        - Multiple LLM provider support
        - ChromaDB memory persistence
        - Structured markdown reports
        """,
        version="1.0.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
    )
    
    # CORS middleware for development
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",  # Vite dev server
            "http://localhost:3000",  # Alternative React port
            "http://127.0.0.1:5173",
            "http://127.0.0.1:3000",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    return app


app = create_app()


# =============================================================================
# Helper Functions
# =============================================================================

def reset_memory_store() -> str:
    """Reset ChromaDB memory for fresh research."""
    try:
        memory_tool = MemoryTool()
        if memory_tool._collection is not None:
            result = memory_tool._clear()
            logger.info(f"Memory reset: {result}")
            return result
        return "Memory not initialized"
    except Exception as e:
        logger.error(f"Failed to reset memory: {e}")
        return f"Failed: {str(e)}"


def run_research_sync(
    ticker: str,
    company_name: Optional[str],
    sequential: bool,
    verbose: bool = False
) -> tuple[str, CrewExecutionResult]:
    """
    Run research workflow synchronously.
    
    This is the core execution function that runs in a thread pool.
    
    Args:
        ticker: Stock ticker symbol
        company_name: Optional company name
        sequential: Whether to use sequential process
        verbose: Enable verbose logging
        
    Returns:
        Tuple of (report_content, execution_result)
    """
    logger.info(f"Starting research for {ticker} (sequential={sequential})")
    
    if sequential:
        crew = SequentialFinResearchCrew(
            ticker=ticker,
            company_name=company_name or ticker,
            verbose=verbose
        )
    else:
        crew = FinResearchCrew(
            ticker=ticker,
            company_name=company_name or ticker,
            verbose=verbose
        )
    
    result = crew.run()
    execution_result = crew.get_execution_result()
    
    # Save report
    crew.save_report(result, filename=f"{ticker}_report.md")
    
    return result, execution_result


async def run_research_async(
    ticker: str,
    company_name: Optional[str],
    sequential: bool
) -> tuple[str, CrewExecutionResult]:
    """
    Run research workflow asynchronously using thread pool.
    
    Args:
        ticker: Stock ticker symbol
        company_name: Optional company name
        sequential: Whether to use sequential process
        
    Returns:
        Tuple of (report_content, execution_result)
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        executor,
        run_research_sync,
        ticker,
        company_name,
        sequential,
        False  # verbose
    )


async def execute_research_task(task_id: str, request: ResearchRequest):
    """
    Background task to execute research and update task store.
    
    Args:
        task_id: Unique task identifier
        request: Research request parameters
    """
    task = task_store.get(task_id)
    if not task:
        logger.error(f"Task {task_id} not found in store")
        return
    
    try:
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.now()
        task.progress_logs.append(f"Starting research for {request.ticker}...")
        
        # Reset memory if requested
        if request.reset_memory:
            task.progress_logs.append("Clearing memory...")
            reset_memory_store()
        
        # Run research
        task.progress_logs.append("Executing agent workflow...")
        report, execution_result = await run_research_async(
            ticker=request.ticker.upper(),
            company_name=request.company_name,
            sequential=request.sequential_mode
        )
        
        # Update task with results
        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.now()
        task.report = report
        task.progress_logs.append("Research completed successfully!")
        
        if execution_result and execution_result.duration_seconds:
            task.progress_logs.append(
                f"Duration: {execution_result.duration_seconds:.1f}s"
            )
        
    except Exception as e:
        logger.exception(f"Research task {task_id} failed")
        task.status = TaskStatus.FAILED
        task.completed_at = datetime.now()
        task.error_message = str(e)
        task.progress_logs.append(f"Error: {str(e)}")


# =============================================================================
# API Routes
# =============================================================================

@app.get("/api/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """
    Health check endpoint.
    
    Returns the API status and version information.
    """
    return HealthResponse()


@app.post("/api/research", response_model=ResearchResponse, tags=["Research"])
async def create_research(request: ResearchRequest):
    """
    Execute a financial research workflow (synchronous).
    
    This endpoint runs the full CrewAI research workflow and returns
    the completed report. For long-running research, consider using
    the async endpoint `/api/research/async`.
    
    Args:
        request: Research parameters including ticker and options
        
    Returns:
        Research response with report content and execution logs
    """
    ticker = request.ticker.strip().upper()
    logs: List[str] = []
    
    # Validate environment
    settings = get_settings()
    if not settings.openai_api_key:
        raise HTTPException(
            status_code=500,
            detail="OPENAI_API_KEY not configured on server"
        )
    
    logs.append(f"Starting research for {ticker}...")
    
    try:
        # Reset memory if requested
        if request.reset_memory:
            logs.append("Resetting memory store...")
            reset_memory_store()
        
        # Run research asynchronously (non-blocking)
        logs.append("Executing agent workflow...")
        report, execution_result = await run_research_async(
            ticker=ticker,
            company_name=request.company_name,
            sequential=request.sequential_mode
        )
        
        logs.append("Research completed successfully!")
        
        return ResearchResponse(
            success=True,
            ticker=ticker,
            report=report,
            logs=logs,
            duration_seconds=execution_result.duration_seconds if execution_result else None,
            error=None
        )
        
    except Exception as e:
        logger.exception(f"Research failed for {ticker}")
        logs.append(f"Error: {str(e)}")
        
        return ResearchResponse(
            success=False,
            ticker=ticker,
            report=None,
            logs=logs,
            error=str(e)
        )


@app.post("/api/research/async", response_model=AsyncResearchResponse, tags=["Research"])
async def create_research_async(
    request: ResearchRequest,
    background_tasks: BackgroundTasks
):
    """
    Initiate an asynchronous research workflow.
    
    Returns a task ID that can be polled via `/api/status/{task_id}`.
    
    Args:
        request: Research parameters
        background_tasks: FastAPI background task handler
        
    Returns:
        Task ID and initial status
    """
    # Validate environment
    settings = get_settings()
    if not settings.openai_api_key:
        raise HTTPException(
            status_code=500,
            detail="OPENAI_API_KEY not configured on server"
        )
    
    # Create task
    task_id = str(uuid.uuid4())
    task = ResearchTask(
        task_id=task_id,
        ticker=request.ticker.upper(),
        status=TaskStatus.PENDING
    )
    task_store[task_id] = task
    
    # Schedule background execution
    background_tasks.add_task(execute_research_task, task_id, request)
    
    return AsyncResearchResponse(
        task_id=task_id,
        status=TaskStatus.PENDING,
        message=f"Research task created for {request.ticker.upper()}"
    )


@app.get("/api/status/{task_id}", response_model=ResearchTask, tags=["Research"])
async def get_task_status(task_id: str):
    """
    Get the status of an async research task.
    
    Args:
        task_id: Task identifier from `/api/research/async`
        
    Returns:
        Current task status, logs, and report (if completed)
    """
    task = task_store.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    
    return task


@app.delete("/api/memory", tags=["System"])
async def clear_memory():
    """
    Clear the ChromaDB memory store.
    
    Useful for starting fresh research without previous context.
    """
    result = reset_memory_store()
    return {"message": result}


# =============================================================================
# Static File Serving (Production)
# =============================================================================

# Path to React build output - supports both local dev and HF Spaces deployment
# HF Spaces: /app/static (copied during Docker build)
# Local dev: ./frontend/dist (built locally)
HF_STATIC_PATH = Path(__file__).parent.parent / "static"
FRONTEND_BUILD_PATH = Path(__file__).parent.parent / "frontend" / "dist"

# Determine which static path to use
def get_static_path() -> Path:
    """Get the correct static files path based on environment."""
    if HF_STATIC_PATH.exists():
        return HF_STATIC_PATH  # Hugging Face Spaces deployment
    return FRONTEND_BUILD_PATH  # Local development

STATIC_PATH = get_static_path()

# Mount static assets immediately if they exist
if STATIC_PATH.exists() and (STATIC_PATH / "assets").exists():
    app.mount(
        "/assets",
        StaticFiles(directory=STATIC_PATH / "assets"),
        name="assets"
    )


@app.on_event("startup")
async def startup_event():
    """Configure app on startup."""
    setup_logging(level="INFO")
    logger.info("FinResearch API starting up...")
    
    # Log frontend status
    if STATIC_PATH.exists():
        logger.info(f"Serving frontend from {STATIC_PATH}")
    else:
        logger.warning(f"Frontend build not found")
        logger.warning("Run 'npm run build' in frontend/ to build the UI")


@app.get("/", tags=["Frontend"])
async def serve_frontend():
    """
    Serve the React frontend application.
    
    In production, this serves the built React app.
    In development, redirect to Vite dev server.
    """
    index_path = STATIC_PATH / "index.html"
    
    if index_path.exists():
        return FileResponse(index_path)
    else:
        # Development mode - frontend served by Vite
        return JSONResponse(
            content={
                "message": "Frontend not built. Use Vite dev server at http://localhost:5173",
                "api_docs": "/api/docs"
            }
        )


@app.get("/vite.svg", tags=["Frontend"])
async def serve_vite_svg():
    """Serve the Vite favicon."""
    # Try HF Spaces path first, then local dev path
    for base_path in [HF_STATIC_PATH, FRONTEND_BUILD_PATH.parent / "public"]:
        svg_path = base_path / "vite.svg" if "static" in str(base_path) else base_path / "vite.svg"
        if svg_path.exists():
            return FileResponse(svg_path, media_type="image/svg+xml")
    raise HTTPException(status_code=404, detail="Favicon not found")


# Catch-all for SPA routing (must be last)
@app.get("/{full_path:path}", tags=["Frontend"])
async def serve_spa(full_path: str):
    """
    Catch-all route for SPA client-side routing.
    
    All non-API routes serve the React app's index.html.
    """
    # Don't interfere with API routes
    if full_path.startswith("api/"):
        raise HTTPException(status_code=404, detail="API endpoint not found")
    
    index_path = STATIC_PATH / "index.html"
    
    if index_path.exists():
        return FileResponse(index_path)
    else:
        raise HTTPException(
            status_code=404,
            detail="Frontend not built. Run 'npm run build' in frontend/"
        )


# =============================================================================
# Development Entry Point
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "src.api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
