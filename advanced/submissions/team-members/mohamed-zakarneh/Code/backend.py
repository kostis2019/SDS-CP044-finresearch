from langchain_openai import ChatOpenAI
from langchain_core.tools import tool, BaseTool
from langchain_community.utilities import SerpAPIWrapper
from langchain_core.documents import Document
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from typing import Type, Any, List, Optional, TypedDict, Annotated, Dict, Tuple
from langchain.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
import yfinance as yf
import requests
import json
from datetime import datetime, timezone
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage
from bs4 import BeautifulSoup
import asyncio
from functools import partial
import time
import math

load_dotenv()


#####################################################################################################################
#                                                                                                                   #
#                                                   Agents Tools                                                    #
#                                                                                                                   #
#####################################################################################################################
### Web Researcher API, Model and Tool ###
search_api = SerpAPIWrapper()
researcher_llm = ChatOpenAI(
    model = 'gpt-5.1',
    temperature= 0
)
reporter_llm = ChatOpenAI(
    model = 'gpt-5.1',
    temperature= 0.2
)
class WebSearchTool(BaseTool):
    name: str = "web_search"
    description: str = "Search the web for company-specific financial context."
    def _run(self, query: str, **kwargs) -> str:
        try:
            results = search_api.results(query)
            lines = ["=== WEB CONTEXT ==="]

            organic = results.get("organic_results", [])
            if len(organic) >= 10:
                organic = organic[:10]
            else:
                organic = organic[:len(organic)]
            link_list =[]
            for r in organic:
                title = r.get("title", "N/A")
                link = r.get("link", "")
                source = r.get("source", "Unknown")
                lines.append(
                    f"- {title}\n"
                    f"  Source: {source}\n"
                    f"  Link: {link}"
                )
                link_list.append(link)
            if len(lines) == 1:
                return "No relevant web context found.", []
            return "\n".join(lines), link_list
        except Exception as e:
            return f"Web search error: {e}", []
    async def _arun(self, query: str):
        raise NotImplementedError("Async version not implemented.")

### Ticker Extractor ###
class ExtractTickerInput(BaseModel):
    query: str = Field(..., description="User request containing a company Name or ticker symbol.")
class TickerExtractionTool(BaseTool):
    name: str = "extract_ticker"
    description: str = (
       "Extract one or multiple ticker symbols from the user query. "
        "Return STRICT JSON: {\"tickers\": [\"AAPL\", \"MSFT\"]}."
    )
    args_schema: Type[BaseModel] = ExtractTickerInput

    def _run(self, query: str, **kwargs) -> str:
        system_message = SystemMessage(content=
                "You extract stock tickers.\n"
                "Return ONLY valid JSON with schema:\n"
                "{\"tickers\": [\"TICKER1\", \"TICKER2\"]}\n"
                "Rules:\n"
                "- If user provides tickers, return them.\n"
                "- If user provides company names, infer tickers.\n"
                "- If none found, return {\"tickers\": []}.\n"
                "- Uppercase tickers, no extra text."
            )
        human_message = HumanMessage(content= query)
        msg = researcher_llm.invoke([system_message, human_message])
        return msg.content

    async def _arun(self, query: str):
        raise NotImplementedError()
def parse_tickers(text: str) -> list[str]:
    try:
        data = json.loads(text)
        if isinstance(data, dict) and "tickers" in data:
            return [t.upper() for t in data["tickers"] if isinstance(t, str)]
    except Exception:
        pass
    return []

### YF Tools ###
class YFTickerInput(BaseModel):
    ticker: str = Field(..., description="Ticker symbol, e.g., AAPL, TSLA, NVDA.")
class EmptyInput(BaseModel):
    pass
class YahooFinanceNewsTool(BaseTool):
    name: str = "yahoo_finance_news"
    description: str = (
        "Fetch latest Yahoo Finance news for a stock ticker. "
        "Returns clean, human-readable headlines."
    )
    args_schema: Type[BaseModel] = YFTickerInput

    def _run(self, ticker: str, **kwargs) -> str:
        try:
            url = "https://query2.finance.yahoo.com/v1/finance/search"
            headers = {
                "User-Agent": "Mozilla/5.0",
                "Accept": "application/json",
            }

            response = requests.get(
                url,
                params={"q": ticker},
                headers=headers,
                timeout=5,
            )

            data = response.json()
            news_items = data.get("news", [])

            if not news_items:
                return f"No recent news found for {ticker}."

            lines = [f"=== LATEST NEWS ({ticker}) ==="]

            for i, item in enumerate(news_items[:5], start=1):
                title = item.get("title", "Untitled")
                publisher = item.get("publisher", "Unknown")
                link = item.get("link", "")
                ts = item.get("providerPublishTime")
                published = (
                    datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M")
                    if ts else "Unknown"
                )
                lines.append(
                    f"{i}. {title}\n"
                    f"   Source: {publisher}\n"
                    f"   Published: {published}\n"
                    f"   Link: {link}\n"
                )

            return "\n".join(lines)

        except Exception as e:
            return f"Error fetching Yahoo Finance news for {ticker}: {e}"

    async def _arun(self, ticker: str):
        raise NotImplementedError("Async not implemented.")
class YahooFinanceStatsTool(BaseTool):
    name: str = "yahoo_finance_stats"
    description: str = (
        "Fetch key financial statistics for a stock ticker from Yahoo Finance. "
        "Includes price data (via fast_info) and fundamentals (via get_stats())."
    )

    args_schema: Type[BaseModel] = YFTickerInput

    def _run(self, ticker: str, **kwargs) -> dict:
        try:
            tk = yf.Ticker(ticker)
            info = tk.info or {}

            return {
                "ticker": ticker.upper(),
                "profile": {
                    "sector": info.get("sector"),
                    "industry": info.get("industry"),
                    "fullTimeEmployees": info.get("fullTimeEmployees"),
                },
                "price": {
                    "previousClose": info.get("previousClose"),
                    "open": info.get("open"),
                    "dayHigh": info.get("dayHigh"),
                    "dayLow": info.get("dayLow"),
                    "allTimeLow": info.get("allTimeLow"),
                    "allTimeHigh": info.get("allTimeHigh"),
                    "fiftyDayAverage": info.get("fiftyDayAverage"),
                    "twoHundredDayAverage": info.get("twoHundredDayAverage"),
                    "fiftyTwoWeekHigh": info.get("fiftyTwoWeekHigh"),
                    "fiftyTwoWeekLow": info.get("fiftyTwoWeekLow"),
                    "volume": info.get("volume"),
                    "regularMarketVolume": info.get("regularMarketVolume"),
                    "averageVolume": info.get("averageVolume"),
                    "averageVolume10days": info.get("averageVolume10days"),
                },
                "fundamentals": {
                    "marketCap": info.get("marketCap"),
                    "beta": info.get("beta"),
                    "ROA": info.get("returnOnAssets"),
                    "ROE": info.get("returnOnEquity"),
                    "trailingPE": info.get("trailingPE"),
                    "forwardPE": info.get("forwardPE"),
                    "trailingEps": info.get("trailingEps"),
                    "forwardEps": info.get("forwardEps"),
                    "totalRevenue": info.get("totalRevenue"),
                    "grossProfits": info.get("grossProfits"),
                    "grossMargins": info.get("grossMargins"),
                    "operatingMargins": info.get("operatingMargins"),
                    "profitMargins": info.get("profitMargins"),
                    "dividendYield": info.get("dividendYield"),
                    "dividendRate": info.get("dividendRate"),
                    "earningsGrowth": info.get("earningsGrowth"),
                    "revenueGrowth": info.get("revenueGrowth")
                },
                "recommendations": {
                    "recommendationKey": info.get("recommendationKey"),
                    "recommendationMean": info.get("recommendationMean"),
                },
                "error": None,
            }

        except Exception as e:
            return {
                "ticker": ticker.upper(),
                "profile": {},
                "price": {},
                "fundamentals": {},
                "recommendations": {},
                "error": str(e),
            }

    async def _arun(self, ticker: str):
        raise NotImplementedError("Async not implemented.")
### TV Tools ###
class TVTickerInput(BaseModel):
    ticker: str = Field(..., description="Ticker symbol, e.g., AAPL, TSLA, NVDA.")
class TradingViewTechnicalTool(BaseTool):
    name: str= "trading_view_technical_summary"
    description: str = (
        "Fetch TradingView technical summary for a ticker, including buy/sell "
        "signals from oscillators and moving averages."
    )
    args_schema: Type[BaseModel] = TVTickerInput

    def _run(self, ticker: str, **kwargs) -> str:
        try:
            url = "https://scanner.tradingview.com/america/scan"
            payload = {
                "symbols": {
                    "tickers": [f"{ticker.upper()}"],
                    "query": {"types": []}
                },
                "columns": [
                    "Recommend.All",
                    "Recommend.MA",
                    "Recommend.Other",
                    "RSI",
                    "MACD.macd",
                    "Stoch.K",
                    "Stoch.D",
                    "ADX",
                    "ADX.DI+",
                    "ADX.DI-",
                ]
            }
            headers = {"Content-Type": "application/json"}
            response = requests.post(url, data=json.dumps(payload), headers=headers)
            data = response.json()
            if not data.get("data"):
                return f"No technical data found for {ticker}."
            row = data["data"][0]["d"]
            return (
                f"Technical Summary for {ticker}:\n"
                f"Overall Recommendation: {row[0]}\n"
                f"Moving Averages Rec: {row[1]}\n"
                f"Oscillators Rec: {row[2]}\n\n"
                f"RSI: {row[3]}\n"
                f"MACD: {row[4]}\n"
                f"Stochastic K: {row[5]}\n"
                f"Stochastic D: {row[6]}\n"
                f"ADX: {row[7]}\n"
                f"DI+: {row[8]}\n"
                f"DI-: {row[9]}\n"
            )
        except Exception as e:
            return f"Error fetching TradingView technical summary for {ticker}: {e}"
    async def _arun(self, ticker: str):
        raise NotImplementedError("Async not implemented.")
class TradingViewTrendingTool(BaseTool):
    name: str = "trading_view_trending"
    description: str = (
        "Fetch trending tickers from TradingView. Useful for identifying market sentiment "
        "and popular stocks based on interest and volume."
    )
    args_schema: Type[BaseModel] = EmptyInput
    def _run(self, **kwargs) -> str:
        try:
            url = "https://symbol-trending.tradingview.com/symbols"
            response = requests.get(url)
            data = response.json()

            if "symbols" not in data:
                return "No trending tickers found."

            symbols = data["symbols"][:15]  # limit to 15 for readability

            formatted = ["Trending Tickers on TradingView:"]
            for s in symbols:
                formatted.append(f"- {s.get('s')}")
            return "\n".join(formatted)

        except Exception as e:
            return f"Error fetching TradingView trending tickers: {e}"
    async def _arun(self):
        raise NotImplementedError("Async not implemented.")
class TradingViewMarketOverviewTool(BaseTool):
    name: str = "trading_view_market_overview"
    description: str = (
        "Fetch market overview data from TradingView, including key index movements, "
        "sector performance, and broad market sentiment."
    )
    args_schema: Type[BaseModel] = EmptyInput
    def _run(self, **kwargs) -> str:
        try:
            url = "https://symbol-overview.tradingview.com/markets"
            response = requests.get(url)
            data = response.json()

            lines = ["TradingView Market Overview"]

            for item in data.get("markets", []):
                name = item.get("name")
                desc = item.get("description")
                lines.append(f"- {name}: {desc}")

            return "\n".join(lines)

        except Exception as e:
            return f"Error fetching TradingView market overview: {e}"

    async def _arun(self):
        raise NotImplementedError("Async not implemented.")

### Memory Tools, Database and Embedding ###
## Memory Tools ##
class MemoryToolInput(BaseModel):
    action: str = Field(..., description="Action to perform: 'save' or 'recall'.")
    text: str = Field("", description="Text to save or query to recall.")
    source: str = Field("unknown", description="Source label for saved memory.")
class MemoryTool(BaseTool):
    name: str = "memory_tool"
    description: str = (
        "Save or recall information from the shared vector memory. "
        "Use action='save' to store text, or action='recall' to search the memory."
    )
    return_direct: bool = False
    args_schema: Type[BaseModel] = MemoryToolInput

    vectorstore: Any
    retriever: Any

    def _run(self, action: str, text: str, source: str = "unknown", **kwargs) -> str:
        # --- SAVE ---
        if action == "save":
            docs = [Document(page_content=text, metadata={"source": source})]
            self.vectorstore.add_documents(docs)
            return f"Saved to memory (source={source})."

        # --- RECALL ---
        elif action == "recall":
            docs = self.retriever.get_relevant_documents(text)
            if not docs:
                return "No relevant items found."
            return "\n\n".join(
                f"[{i+1}] ({d.metadata.get('source','?')}): {d.page_content}"
                for i, d in enumerate(docs)
            )

        # --- INVALID ---
        else:
            return "Invalid action. Use 'save' or 'recall'."

    async def _arun(self, **kwargs):
        raise NotImplementedError("Async not implemented yet.")
## Embeddings and Databse ##   
embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
vectorstore = Chroma(
    collection_name="shared_research",
    embedding_function=embeddings,
    persist_directory="chroma_shared_memory"
)
retriever = vectorstore.as_retriever(search_kwargs={"k": 6})
## Initilizing the Researcher Tools ##
memory_tool = MemoryTool(vectorstore=vectorstore, retriever=retriever)
web_search_tool = WebSearchTool()
yf_news_tool = YahooFinanceNewsTool()
yf_stats_tool = YahooFinanceStatsTool()
tv_tech_tool = TradingViewTechnicalTool()
tv_trending_tool = TradingViewTrendingTool()
tv_market_tool = TradingViewMarketOverviewTool()
ticker_exctracter = TickerExtractionTool()
#####################################################################################################################
#                                                                                                                   #
#                                                   LangGraph                                                       #
#                                                                                                                   #
#####################################################################################################################
PER_TICKER_TOOLS = [web_search_tool, yf_news_tool, yf_stats_tool, tv_tech_tool]
PER_REQ_TOOLS = [tv_trending_tool, tv_market_tool]
###### State Definition
class GraphState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    tickers: Optional[List[str]]
    objective: Optional[str]        # What the user is looking for. Single Company report or Multi-Companies Comparison and reporting    

    # Raw tool outputs (store exactly what tools returned)
    ticker_extracted: List[str]          # e.g ['AAPL', 'MSFT', ...] 
    researcher_outputs: Dict[str, Any]   # e.g. {"AAPL": {...}, "MSFT": {...}}
    analyst_outputs: Dict[str, Any]      # ratios/metrics computed

    # Shared memory bookkeeping (optional but useful)
    memory_saved: Optional[List[str]]    # e.g. list of saved snippet IDs/labels
    # Final deliverables
    final_report: Optional[str]
###### Nodes Definition
def manager_node(state: GraphState) -> GraphState:
    user_msg = state["messages"][-1].content.lower()
    system_msg = SystemMessage(content=
                               """You are a manager routing agent for a financial research system.
                                  you MUST output ONLY valid JSON (no markdown, no extra text).
                                 Schema:
                                 {
                                 "route": "reject" | "clarify" | "single_company" | "comparison",
                                 "reason": "short string"
                                 }
                                 Rules:
                                 1) If the user request is NOT about finance/markets/investing/company financials -> route="reject".
                                 2) If it IS financial but has no specific company names/tickers -> route="clarify".
                                 3) If it IS financial and mentions exactly one company/ticker -> route="single_company".
                                 4) If it IS financial and mentions multiple companies/tickers -> route="comparison".
                                 Return JSON only.""")
    decision = researcher_llm.invoke([system_msg, HumanMessage(user_msg)])
    decision_text = decision.content
    objective = parse_manager_output(decision_text)
    return {
        **state,
        #"objective": objective['route'],
        "objective": objective,
        "messages": state["messages"] + [decision]}
def parse_manager_output(text: str) -> dict:
    try:
        data = json.loads(text)
        if data['route'] in ["reject", "clarify", "single_company", "comparison"]:
            return data
    except Exception:
        pass
    # Safe fallback if model misbehaves
    return {
        "route": "reject",
        "reason": "Invalid manager output"
    }
def route_from_manager(state: GraphState) -> str:
    manager_msg = state["messages"][-1].content
    parsed = parse_manager_output(manager_msg)
    return parsed['route']
def researcher_node(state: GraphState) -> GraphState:
    user_query = state["messages"][-1].content
    # 1) Extract tickers FIRST (single call)
    raw = ticker_exctracter.run({'query':user_query})
    tickers = parse_tickers(raw)

    if not tickers:
        return {
            **state,
            "messages": state["messages"] + [
                SystemMessage(content="No valid ticker symbols found.")
            ],
        }
    # 2) Run per-query tools
    query_context = run_async(run_query_tools_async(PER_REQ_TOOLS))
    # 3) Run all tickers + tools in parallel
    ticker_results = run_async(run_all_tickers_async(tickers=tickers, user_query=user_query, tools=PER_TICKER_TOOLS))
    # 4) Fetch Web Pages Content in parrallel
    for ticker, tools_out in ticker_results.items():
        web_out = tools_out.get("web_search")

        if isinstance(web_out, tuple) and len(web_out) == 2:
            _, links = web_out

            if links:
                pages = run_async(fetch_pages_parallel(links))
                tools_out["web_pages"] = pages
            else:
                tools_out["web_pages"] = []

    return {
        **state,
        "tickers": tickers,
        "ticker_extracted": tickers,
        "researcher_outputs": {
            "market_context": query_context,
            "companies": ticker_results,
        },
        "messages": state["messages"],
    }
def analyst_node(state: GraphState) -> GraphState:
    tickers = state.get("tickers") or state.get("ticker_extracted") or []
    outputs: Dict[str, Any] = {}
    for t in tickers:
        try:
            company_block, market_context = _get_company_block(state, t)
            stats_raw = company_block.get("yahoo_finance_stats")
            stats = _coerce_stats(stats_raw)
            profile = stats.get("profile", {}) or {}
            fundamentals = stats.get("fundamentals", {}) or {}
            recommendations = stats.get("recommendations", {}) or {}
            trailingEps = _safe_float(fundamentals.get("trailingEps"))
            forwardEps = _safe_float(fundamentals.get("forwardEps"))
            trailingPE = _safe_float(fundamentals.get("trailingPE"))
            forwardPE = _safe_float(fundamentals.get("forwardPE"))
            earningsGrowth = _safe_float(fundamentals.get("earningsGrowth"))

            peg_ratio = _calc_peg(trailingEps, forwardEps, trailingPE, forwardPE, earningsGrowth)

            base = {
                "ticker": t.upper(),
                "sector": profile.get("sector"),
                "industry": profile.get("industry"),
                "market_cap": _safe_float(fundamentals.get("marketCap")),
                "beta": _safe_float(fundamentals.get("beta")),
                "trailing_pe": trailingPE,
                "forward_pe": forwardPE,
                "peg_ratio": peg_ratio,
                "roe": _safe_float(fundamentals.get("ROE") or stats.get("ROE")),
                "roa": _safe_float(fundamentals.get("ROA") or stats.get("ROA")),
                "revenue_growth": _safe_float(fundamentals.get("revenueGrowth") or stats.get("revenueGrowth")),
                "earnings_growth": earningsGrowth,
                "dividend_yield": _safe_float(fundamentals.get("dividendYield")),
                "recommendation_key": recommendations.get("recommendationKey"),
                "recommendation_mean": _safe_float(recommendations.get("recommendationMean")),
            }
            risk = _calc_risk_metrics(t)
            outputs[t.upper()] = {
                **base,
                **risk,
                "market_context_used": bool(market_context),
                "source": "researcher_outputs + calculated_risk",
                "error": stats.get("error"),
            }

        except Exception as e:
            outputs[t.upper()] = {"ticker": t.upper(), "error": str(e)}

    return {**state, "analyst_outputs": outputs, "messages": state["messages"]}
def report_node(state: GraphState) -> GraphState:
    user_message = state.get("messages")
    objective = state.get("objective")
    tickers = state.get("tickers") or state.get("ticker_extracted") or []
    ro = state.get("researcher_outputs") or {}
    analyst = state.get("analyst_outputs") or {}

    # Keep context compact
    context = {
        "user_message": user_message,
        "objective": objective,
        "tickers": tickers,
        "market_context": ro.get("market_context", {}),
        "companies_tools": ro.get("companies", {}),
        "analyst_outputs": analyst,
    }

    system = SystemMessage(content=
        "You are a reporting agent. Write a professional investment-style report.\n"
        "Use ONLY the provided context. If something is missing, say 'N/A'.\n"
        "Output Markdown with clear sections and bullet points.\n"
        "If objective='comparison', include a comparison table across tickers.\n"
    )

    human = HumanMessage(content=f"CONTEXT (JSON):\n{json.dumps(context, default=str)[:120000]}")
    msg = reporter_llm.invoke([system, human])
    final_text = msg.content.strip() if msg.content else "No report generated."
    return {
        **state,
        "final_report": final_text,
        "messages": state["messages"] + [msg],
    }

#######LangGraph Graph
graph = StateGraph(GraphState)
graph.add_node("manager", manager_node)
graph.add_node("researcher", researcher_node)
graph.add_node("analyst", analyst_node)
graph.add_node("report", report_node)
graph.set_entry_point("manager")
graph.add_conditional_edges("manager", route_from_manager, {
        "reject": END,
        "clarify": END,
        "single_company": "researcher",
        "comparison": "researcher"})
graph.add_edge("researcher", "analyst")
graph.add_edge("analyst", "report")
graph.add_edge("report", END)

app = graph.compile()

##################################
#                                #
#       Parralel Functions       #
#                                #    
##################################
async def run_tool_async(tool, tool_input: dict):
        start = time.time()
        print(f"[START] Tool={tool.name}, kwargs={tool_input}")

        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(None, partial(tool.run, tool_input))

        duration = round(time.time() - start, 2)
        print(f"[END]   Tool={tool.name}, took {duration}s")
        return result
async def run_tools_for_ticker_async(ticker: str, user_query: str, tools: List) -> dict:
    tasks = {}
    for tool in tools:
        # Decide how to call the tool
        if tool.name == "web_search":
            tool_input  = {"query": f"{ticker} company financial performance"}
        else:
            tool_input  = {"ticker": ticker}

        # Start the tool asynchronously
        tasks[tool.name] = asyncio.create_task(
            run_tool_async(tool, tool_input )        )
    results = {}

    # Collect results safely
    for tool_name, task in tasks.items():
        try:
            results[tool_name] = await task
        except Exception as e:
            results[tool_name] = f"ERROR: {e}"
    return results
async def run_all_tickers_async(tickers: list[str], user_query: str, tools: List,) -> dict:
    tasks = {}
    # Start all tickers in parallel
    for ticker in tickers:
        tasks[ticker] = asyncio.create_task(
            run_tools_for_ticker_async(ticker, user_query, tools))
    results = {}
    # Collect results safely
    for ticker, task in tasks.items():
        try:
            results[ticker] = await task
        except Exception as e:
            results[ticker] = {"ERROR": str(e)}
    return results
async def run_query_tools_async(tools: List) -> dict:
    tasks = {tool.name: asyncio.create_task(run_tool_async(tool, {})) for tool in tools}
    results = {}
    for name, task in tasks.items():
        try:
            results[name] = await task
        except Exception as e:
            results[name] = f"ERROR: {e}"
    return results
async def fetch_pages_parallel(urls: list[str]) -> list[dict]:
    loop = asyncio.get_running_loop()

    tasks = [
        loop.run_in_executor(None, fetch_and_clean_page, url)
        for url in urls
        if url
    ]
    return await asyncio.gather(*tasks)
def run_async(corot):
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(corot)
    return loop.run_until_complete(corot)
##################################
#                                #
#     Researcher Functions       #
#                                #    
##################################
def fetch_and_clean_page(url: str, timeout: int = 6) -> dict:
    """
    Fetch a web page and return cleaned text content.
    """
    try:
        resp = requests.get(
            url,
            timeout=timeout,
            headers={"User-Agent": "Mozilla/5.0"}
        )
        if resp.status_code != 200:
            return {"url": url, "error": f"HTTP {resp.status_code}"}
        soup = BeautifulSoup(resp.text, "html.parser")
        # Remove junk
        for tag in soup(["script", "style", "noscript", "header", "footer", "nav"]):
            tag.decompose()
        text = soup.get_text(separator=" ", strip=True)
        # Light sanity filter
        if len(text) < 500:
            return {"url": url, "error": "Content too short"}
        return {
            "url": url,
            "content": text[:8000]  # cap to avoid explosions
        }
    except Exception as e:
        return {"url": url, "error": str(e)}
##################################
#                                #
#        Analyst Functions       #
#                                #    
##################################
def _get_company_block(state: GraphState, ticker: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    ro = state.get("researcher_outputs") or {}
    companies = ro.get("companies") or ro.get("Companies") or {}
    market_cont = ro.get("market_context") or ro.get("Market_Context") or {}

    # ticker keys might be uppercase depending on your extraction
    company = companies.get(ticker) or companies.get(ticker.upper()) or {}

    return company, market_cont
def _coerce_stats(stats_obj) -> dict:
    if isinstance(stats_obj, dict):
        return stats_obj
    if isinstance(stats_obj, str):
        s = stats_obj.strip()
        try:
            parsed = json.loads(s)
            if isinstance(parsed, dict):
                return parsed
        except Exception:
            return {}
    return {}
def _safe_float(x):
    try:
        if x is None:
            return None
        return float(x)
    except Exception:
        return None
def _calc_risk_metrics(ticker: str) -> dict:
    tk = yf.Ticker(ticker)
    hist = tk.history(period="1y", interval="1d")

    if hist is None or hist.empty or "Close" not in hist:
        return {"volatility_1y": None, "annual_return_1y": None, "max_drawdown_1y": None}

    close = hist["Close"].dropna()
    rets = close.pct_change().dropna()

    if rets.empty:
        return {"volatility_1y": None, "annual_return_1y": None, "max_drawdown_1y": None}

    vol = float(rets.std() * math.sqrt(252))
    ann_ret = float((1 + rets.mean()) ** 252 - 1)

    running_max = close.cummax()
    dd = (close / running_max - 1.0)
    max_dd = float(dd.min())

    return {
        "volatility_1y": vol,
        "annual_return_1y": ann_ret,
        "max_drawdown_1y": max_dd,
    }
def _calc_peg(trailingEps, forwardEps, trailingPE, forwardPE, earningsGrowth):
    if earningsGrowth is not None and earningsGrowth > 0:
        growth_pct = earningsGrowth * 100
        return trailingPE / growth_pct

    # fallback to forward EPS growth
    if trailingEps and forwardEps and trailingEps > 0:
        eps_growth_pct = ((forwardEps - trailingEps) / trailingEps) * 100
        if eps_growth_pct > 0:
            return forwardPE / eps_growth_pct

    return None  # PEG not meaningful

##################################
#                                #
#        Streamlit Entry         #
#                                #    
##################################

def run_financial_agent(user_query: str) -> dict:
    state = {
        "messages": [HumanMessage(content=user_query)],
        "tickers": None,
        "objective": None,
        "ticker_extracted": [],
        "researcher_outputs": {},
        "analyst_outputs": {},
        "memory_saved": [],
        "final_report": None,
    }
    result = app.invoke(state)
    return {
        "objective": result.get("objective"),
        "tickers": result.get("tickers") or result.get("ticker_extracted"),
        "analyst_outputs": result.get("analyst_outputs"),
        "final_report": result.get("final_report"),
        "raw_state": result,  # useful for debugging later
    }



