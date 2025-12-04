# FinResearch AI - Advanced Track
## Multi-Agent Financial Research System

### Project Overview
This is a production-grade, multi-agent financial research system capable of autonomously gathering data, analyzing ratios, extracting insights, and generating polished investor-style reports.

### Architecture
The system consists of four specialized agents:
- **Manager Agent**: Orchestrates the entire workflow and delegates tasks
- **Researcher Agent**: Fetches market news and web content
- **Financial Analyst Agent**: Computes financial ratios and metrics
- **Reporting Agent**: Synthesizes findings into a comprehensive report

All agents share a vector memory (ChromaDB) for efficient context retrieval.

### Project Structure
```
.
├── agents/              # Agent implementations
├── memory/              # Vector database and memory management
├── utils/               # Helper functions and utilities
├── config/              # Configuration files
├── app.py              # Gradio UI interface
├── requirements.txt    # Python dependencies
└── .env.example        # Environment variables template
```

### Setup Instructions
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and add your API keys
4. Run the application: `python app.py`

### API Keys Required
- `OPENAI_API_KEY`: For LLM capabilities
- `TAVILY_API_KEY` or `SERPAPI_API_KEY`: For web search
- `ALPHAVANTAGE_API_KEY` or `FMP_API_KEY`: For financial data (or use yfinance without key)

### Features
- Real-time financial data analysis
- News and sentiment analysis
- Multi-ratio computation (P/E, PEG, Debt/Equity, etc.)
- Vector memory for context persistence
- Professional financial report generation
- Interactive Gradio UI

### Status
🚧 In Development

### Author
Art Turner
