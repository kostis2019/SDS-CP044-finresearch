# FinResearch AI - Advanced Track

## Multi-Agent Financial Research System

A production-grade, hierarchical multi-agent system for automated financial research, built with CrewAI. This implementation serves as the gold standard reference for the FinResearch AI project.

**Key Features:**
- 🚀 **Parallel Execution** - Research and Analysis run simultaneously for faster results
- 💬 **Interactive Mode** - Conversational interface with context persistence
- 🧠 **Memory System** - ChromaDB-powered context sharing between agents
- 📊 **Professional Reports** - Markdown reports with validation

---

## System Architecture

```
                              INPUT
                    ┌─────────────────────┐
                    │   CLI (main.py)     │
                    │   Interactive Mode  │
                    │   Config (.env)     │
                    └──────────┬──────────┘
                               │
                               ▼
                         ORCHESTRATION
                    ┌─────────────────────┐
                    │   FinResearchCrew   │
                    │     (crew.py)       │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Manager Agent     │
                    │   (Orchestrator)    │
                    └──────────┬──────────┘
                               │
            ┌──────────────────┴──────────────────┐
            │          PARALLEL EXECUTION         │
            │                                     │
            ▼                                     ▼
     ┌─────────────┐                       ┌─────────────┐
     │ Researcher  │     (async)           │  Analyst    │
     │ Qualitative │◄────────────────────►│ Quantitative│
     └──────┬──────┘                       └──────┬──────┘
            │                                     │
            │         ┌─────────────┐             │
            └────────►│ ChromaDB    │◄────────────┘
                      │ (Memory)    │
                      └──────┬──────┘
                             │
                             ▼
                      ┌─────────────┐
                      │  Reporter   │
                      │  (Waits for │
                      │   both)     │
                      └──────┬──────┘
                             │
                             ▼
                    ┌─────────────────────┐
                    │  Markdown Report    │
                    │   (./outputs/)      │
                    └─────────────────────┘
```

---

## Directory Structure

```
yan-cotta/
├── main.py                 # CLI entry point
├── verify_full_run.py      # End-to-end verification script
├── pyproject.toml          # Project metadata and dependencies
├── Dockerfile              # Container configuration
├── .dockerignore           # Docker build exclusions
├── .gitignore              # Git exclusions
├── README.md               # This documentation
│
├── src/
│   ├── __init__.py
│   ├── crew.py             # Crew orchestration logic
│   │
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py     # Pydantic settings management
│   │   ├── agents.yaml     # Agent personas and prompts
│   │   └── tasks.yaml      # Task templates
│   │
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base.py         # Base factory and utilities
│   │   ├── manager.py      # Manager agent (orchestrator)
│   │   ├── researcher.py   # Researcher agent (qualitative)
│   │   ├── analyst.py      # Analyst agent (quantitative)
│   │   └── reporter.py     # Reporter agent (synthesis + ReportOutput model)
│   │
│   └── tools/
│       ├── __init__.py
│       ├── base.py         # Base tool classes
│       ├── financial_data.py   # Yahoo Finance wrapper
│       ├── news_search.py      # DuckDuckGo wrapper
│       └── memory.py           # ChromaDB memory tool
│
├── outputs/                # Generated reports (gitignored)
│   └── .gitkeep
│
└── tests/
    ├── __init__.py
    └── test_financial_tool.py  # Tool unit tests
```

---

## Module Overview

### Configuration (`src/config/`)

| File | Purpose |
|------|---------|
| `settings.py` | Pydantic-based settings with environment variable support |
| `agents.yaml` | Agent roles, goals, and backstories (prompts) |
| `tasks.yaml` | Task description templates with placeholders |

### Tools (`src/tools/`)

| Tool | Data Source | Purpose |
|------|-------------|---------|
| `FinancialDataTool` | Yahoo Finance | Stock prices, valuation metrics, fundamentals |
| `NewsSearchTool` | DuckDuckGo | News articles with source verification |
| `MemoryTool` | ChromaDB | Persistent vector memory for agent collaboration |

### Agents (`src/agents/`)

| Agent | Role | Temperature | Tools |
|-------|------|-------------|-------|
| Manager | Orchestration and delegation | 0.1 | Memory |
| Researcher | Qualitative analysis | 0.7 | News, Memory |
| Analyst | Quantitative analysis | 0.0 | Financial, Memory |
| Reporter | Report synthesis | 0.5 | Memory |

### Crew Orchestration (`src/crew.py`)

Provides two execution modes:

- `FinResearchCrew`: Hierarchical process with Manager delegation
- `SequentialFinResearchCrew`: Linear task execution (for debugging)

---

## Setup Instructions

### Prerequisites

- Python 3.10 or higher
- OpenAI API key
- Virtual environment (recommended)

### Installation

```bash
# Navigate to this directory
cd advanced/submissions/team-members/yan-cotta

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -e .
```

### Configuration

Create a `.env` file in the project root:

```env
# Required
OPENAI_API_KEY=sk-your-openai-api-key

# Optional overrides
FINRESEARCH_MANAGER_MODEL=gpt-4o-mini
FINRESEARCH_WORKER_MODEL=gpt-3.5-turbo
FINRESEARCH_LOG_LEVEL=INFO
FINRESEARCH_OUTPUT_DIR=./reports
```

---

## Usage

### Command Line Interface

```bash
# Research Apple Inc
python main.py AAPL

# Research with company name
python main.py TSLA --name "Tesla Inc"

# Use sequential process (simpler, for debugging)
python main.py MSFT --sequential

# Custom output filename
python main.py GOOGL --output google_research.md

# Verbose mode (see agent reasoning)
python main.py NVDA --verbose
```

### CLI Options

```
positional arguments:
  ticker                Stock ticker symbol (e.g., AAPL, TSLA)

optional arguments:
  -i, --interactive     Start interactive conversational mode
  -n, --name            Company name (defaults to ticker)
  -o, --output          Output filename for report
  -s, --sequential      Use sequential instead of hierarchical process
  -v, --verbose         Enable verbose agent output
  -q, --quiet           Suppress banner and progress
  --log-level           Logging level (DEBUG/INFO/WARNING/ERROR)
  --log-file            Log to file instead of stdout
  --dry-run             Validate config without running
  --reset-memory        Clear ChromaDB before starting
  --json-output         Output result as JSON (for UI integration)
```

---

## Interactive Mode

Start the conversational interface for multi-query research sessions:

```bash
# Start interactive mode
python main.py --interactive
# or
python main.py -i
```

### Interactive Commands

| Command | Description |
|---------|-------------|
| `AAPL` | Research a ticker |
| `research TSLA` | Research Tesla |
| `analyze MSFT` | Analyze Microsoft |
| `context` | Show context for current ticker |
| `context AAPL` | Show context for specific ticker |
| `status` | Show session summary |
| `clear` | Start fresh session |
| `help` | Show all commands |
| `exit` / `quit` | Exit interactive mode |

### Follow-up Queries

When you have an active ticker, you can ask follow-up questions:

```
finresearch[AAPL]> more details
finresearch[AAPL]> what about risks
finresearch[AAPL]> research TSLA    # Switch to new ticker
```

### Context Persistence

Interactive mode uses ChromaDB to maintain context:
- Previous research findings are stored
- Follow-up queries can access prior context
- Session history tracks all queries

---

## Parallel Execution

Research and Analysis tasks run simultaneously for improved performance:

```yaml
# tasks.yaml configuration
research_task:
  async_execution: true  # Run in parallel

analysis_task:
  async_execution: true  # Run in parallel

report_task:
  # Waits for both via context dependency
```

**Benefits:**
- ~40% faster execution for typical queries
- Researcher and Analyst work independently
- Reporter synthesizes both results when ready

### Python API

```python
from src.crew import FinResearchCrew

# Create and run crew
crew = FinResearchCrew(
    ticker="AAPL",
    company_name="Apple Inc",
    verbose=True
)

# Execute research
report = crew.run()

# Save report
path = crew.save_report(report)
print(f"Report saved to: {path}")
```

### Docker

```bash
# Build image
docker build -t finresearch-advanced .

# Run research
docker run -e OPENAI_API_KEY=sk-... finresearch-advanced AAPL
```

---

## Workflow

```
User                Manager             Researcher          Analyst             Reporter            Memory
 │                     │                    │                   │                   │                  │
 │  Research AAPL      │                    │                   │                   │                  │
 │────────────────────>│                    │                   │                   │                  │
 │                     │                    │                   │                   │                  │
 │                     │  Find news         │                   │                   │                  │
 │                     │───────────────────>│                   │                   │                  │
 │                     │                    │                   │                   │                  │
 │                     │                    │  Save findings    │                   │                  │
 │                     │                    │─────────────────────────────────────────────────────────>│
 │                     │                    │                   │                   │                  │
 │                     │  Research done     │                   │                   │                  │
 │                     │<───────────────────│                   │                   │                  │
 │                     │                    │                   │                   │                  │
 │                     │  Get financials    │                   │                   │                  │
 │                     │──────────────────────────────────────>│                   │                  │
 │                     │                    │                   │                   │                  │
 │                     │                    │                   │  Save metrics     │                  │
 │                     │                    │                   │──────────────────────────────────────>│
 │                     │                    │                   │                   │                  │
 │                     │  Analysis done     │                   │                   │                  │
 │                     │<──────────────────────────────────────│                   │                  │
 │                     │                    │                   │                   │                  │
 │                     │  Create report     │                   │                   │                  │
 │                     │─────────────────────────────────────────────────────────>│                  │
 │                     │                    │                   │                   │                  │
 │                     │                    │                   │                   │  Get all data    │
 │                     │                    │                   │                   │─────────────────>│
 │                     │                    │                   │                   │                  │
 │                     │  Report ready      │                   │                   │                  │
 │                     │<─────────────────────────────────────────────────────────│                  │
 │                     │                    │                   │                   │                  │
 │  Final report       │                    │                   │                   │                  │
 │<────────────────────│                    │                   │                   │                  │
 │                     │                    │                   │                   │                  │
```

---

## Output Example

Reports are saved to `./outputs/` with the format:

```
AAPL_report.md
```

Sample report structure:

```markdown
# Investment Research Report: Apple Inc (AAPL)

**Generated:** 2024-12-17 14:30:52

---

## Executive Summary
...

## Market Data & Financial Metrics
...

## News Analysis & Recent Developments
...

## Risk Assessment
...

---

## Disclaimer
*This report is for informational purposes only...*
```

---

## Verification Script

Run the end-to-end verification to test the complete workflow:

```bash
# Run full verification for NVDA
python verify_full_run.py

# Test with custom ticker
python verify_full_run.py --ticker AAPL

# Dry run (validate setup only)
python verify_full_run.py --dry-run

# Test interactive mode components
python verify_full_run.py --test-interactive

# Verbose output
python verify_full_run.py -v
```

The verification script checks:

1. All imports resolve correctly
2. Configuration files are valid
3. Environment variables are set
4. ChromaDB memory tool works
5. All agents can be created
6. Output directory is writable
7. Parallel execution is configured
8. Interactive mode query parsing works
9. Conversation context management works
10. Crew executes successfully
11. Report is generated with required sections

---

## Design Decisions

### Why Hierarchical Process?

The Manager agent coordinates work, ensuring:

- Proper task sequencing
- Quality control before final output
- Efficient delegation to specialists

### Why Separate Tools per Agent?

- **Prevents hallucination**: Analyst cannot fabricate news articles
- **Clear responsibilities**: Each agent has focused expertise
- **Easier debugging**: Issues are isolated to specific agents

### Why ChromaDB Memory?

- Enables agent collaboration without direct communication
- Persists context across task boundaries
- Supports semantic retrieval for relevant information

---

## Testing

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test
pytest tests/test_financial_tool.py -v
```

---

## Troubleshooting

### OPENAI_API_KEY not configured

Ensure your `.env` file is in the project root and contains a valid key.

### No data found for ticker

Verify the ticker symbol is valid on Yahoo Finance.

### ChromaDB not installed

Run: `pip install chromadb`

### Agent seems stuck

Use `--sequential` mode for simpler execution and easier debugging.

---

## License

MIT License - See project root for details.

---

**Author:** Yan Cotta

**Version:** 1.0.0

**Last Updated:** December 2025
