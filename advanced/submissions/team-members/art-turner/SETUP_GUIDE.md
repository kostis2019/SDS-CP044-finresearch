# FinResearch AI - Quick Setup Guide

## Prerequisites

- Python 3.10 or higher
- pip package manager
- API keys (at minimum: OpenAI API key)

## Step-by-Step Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install all required packages including:
- OpenAI for LLM capabilities
- LangChain for agent framework
- ChromaDB for vector memory
- Gradio for UI
- yfinance for financial data
- And more...

### 2. Configure API Keys

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```bash
# Required
OPENAI_API_KEY=sk-your-openai-api-key-here

# Optional (recommended for better news search)
TAVILY_API_KEY=your-tavily-api-key-here

# Optional (alternative search)
SERPAPI_API_KEY=your-serpapi-key-here

# Optional (enhanced financial data)
ALPHAVANTAGE_API_KEY=your-alphavantage-key-here
```

**Minimum Required:** Only `OPENAI_API_KEY` is required. The system will use fallback options for other features.

### 3. Get API Keys

#### OpenAI (Required)
1. Go to https://platform.openai.com/
2. Sign up or log in
3. Navigate to API Keys
4. Create new secret key
5. Copy and paste into `.env`

#### Tavily (Recommended for news)
1. Go to https://tavily.com/
2. Sign up for free account
3. Get your API key from dashboard
4. Copy and paste into `.env`

#### SerpAPI (Alternative for news)
1. Go to https://serpapi.com/
2. Sign up for free account (100 searches/month)
3. Get your API key
4. Copy and paste into `.env`

#### Alpha Vantage (Optional for enhanced data)
1. Go to https://www.alphavantage.co/
2. Get free API key
3. Copy and paste into `.env`

### 4. Run the Application

```bash
python app.py
```

The application will:
- Validate your configuration
- Initialize all agents
- Start the Gradio web interface
- Open automatically in your browser at http://localhost:7860

### 5. Use the Application

1. Enter a stock ticker (e.g., AAPL, TSLA, MSFT)
2. Select investor mode (Neutral, Bullish, or Bearish)
3. Click "Generate Report"
4. Wait 45-70 seconds for comprehensive analysis
5. View results in tabs
6. Download reports in Markdown or JSON format

## Troubleshooting

### Error: "OPENAI_API_KEY is required"

**Solution:** Make sure you've created a `.env` file and added your OpenAI API key.

### Error: "No module named 'openai'"

**Solution:** Run `pip install -r requirements.txt` to install dependencies.

### Warning: "No search API key found"

**Solution:** This is just a warning. The system will use yfinance news as a fallback. For better results, add Tavily or SerpAPI key.

### Error: "Ticker validation failed"

**Solution:**
- Check that you entered a valid ticker symbol
- Try a major ticker like AAPL or MSFT
- Check your internet connection

### Slow Performance

**Solution:**
- First run creates ChromaDB database (slower)
- Subsequent runs are faster
- Free API tiers may have rate limits
- Consider upgrading to paid API tiers

## Project Structure

```
art-turner/
├── agents/              # AI agent implementations
│   ├── manager_agent.py         # Orchestrator
│   ├── researcher_agent.py      # News & sentiment
│   ├── analyst_agent.py         # Financial analysis
│   └── reporting_agent.py       # Report generation
├── memory/              # Vector database
│   └── vector_store.py          # ChromaDB wrapper
├── utils/               # Helper utilities
│   ├── api_clients.py           # API integrations
│   └── formatters.py            # Data formatting
├── config/              # Configuration
│   └── settings.py              # Settings management
├── app.py              # Main Gradio application
├── requirements.txt    # Python dependencies
├── .env.example       # Environment template
├── README.md          # Project overview
├── REPORT.md          # Detailed documentation
└── SETUP_GUIDE.md     # This file
```

## Example Usage

### Analyzing Apple (AAPL)

1. Enter ticker: `AAPL`
2. Mode: `Neutral`
3. Click "Generate Report"

**Expected Output:**
- Executive summary of Apple's current position
- 20+ financial metrics and ratios
- Recent news and sentiment analysis
- Bull case highlighting growth opportunities
- Bear case outlining risks
- Final balanced perspective

### Analyzing Tesla (TSLA) with Bullish Tone

1. Enter ticker: `TSLA`
2. Mode: `Bullish`
3. Click "Generate Report"

**Expected Output:**
- Emphasis on growth potential and opportunities
- Positive framing of metrics
- Still includes risks but focuses on upside

## Advanced Features

### Vector Memory

All research is stored in ChromaDB at `./chroma_db/`. This allows:
- Context persistence across sessions
- Semantic search of findings
- Historical analysis

To clear the database:
```python
from agents.manager_agent import ManagerAgent
manager = ManagerAgent()
manager.clear_all_data()
```

### Parallel Execution

By default, the Researcher and Analyst agents run in parallel for faster results. To run sequentially:

```python
result = manager.conduct_research(ticker, parallel=False)
```

### Custom Investor Modes

Three modes available:
- **Neutral:** Balanced analysis (default)
- **Bullish:** Optimistic tone, emphasizes opportunities
- **Bearish:** Cautious tone, emphasizes risks

## Next Steps

1. **Experiment with different tickers:** Try various stocks across different sectors
2. **Compare investor modes:** See how the tone changes between neutral/bullish/bearish
3. **Review the code:** Explore how agents collaborate through vector memory
4. **Customize reports:** Modify formatting in `agents/reporting_agent.py`
5. **Add new metrics:** Extend `agents/analyst_agent.py` with additional analysis

## Support & Resources

- **Project README:** See `README.md` for overview
- **Detailed Documentation:** See `REPORT.md` for architecture details
- **Code Documentation:** Check docstrings in all Python files
- **FinResearch Project:** See main project README at repository root

## Deployment Options

### Hugging Face Spaces

1. Create new Space on huggingface.co
2. Upload all project files
3. Add secrets (API keys) in Settings
4. Space will auto-deploy

### Streamlit Cloud

1. Push code to GitHub
2. Connect repository to Streamlit Cloud
3. Add secrets via dashboard
4. Deploy

### Docker (Optional)

Create `Dockerfile`:
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "app.py"]
```

## License & Disclaimer

This is an educational project demonstrating multi-agent AI systems. The financial analysis provided is AI-generated and should not be considered financial advice. Always consult with a qualified financial advisor before making investment decisions.

---

**Happy Analyzing! 📊🚀**
