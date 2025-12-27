# tools/news_tools.py
# News search tools with proper error handling
# ---------------------------------------------

import os
from typing import List, Dict
import requests
from crewai.tools import tool


def _tavily_search_logic(query: str, max_results: int) -> List[Dict]:
    """Internal logic for Tavily search."""
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return [{"error": "TAVILY_API_KEY not set."}]

    url = "https://api.tavily.com/search"
    payload = {
        "api_key": api_key,
        "query": query,
        "search_depth": "advanced",
        "max_results": max_results,
    }

    try:
        r = requests.post(url, json=payload, timeout=20)
        if r.status_code == 401:
            return [{"error": "Invalid Tavily API key."}]
        r.raise_for_status()

        results = r.json().get("results", [])
        if not results:
            return []  # Return empty list, not error dict

        return [
            {
                "title": item.get("title"),
                "content": item.get("content"),
                "source": item.get("url"),
            }
            for item in results
        ]
    except requests.exceptions.RequestException as e:
        return [{"error": f"Tavily error: {str(e)}"}]


def _serpapi_search_logic(query: str, max_results: int) -> List[Dict]:
    """Internal logic for SerpAPI search."""
    api_key = os.getenv("SERPAPI_API_KEY")
    if not api_key:
        return [{"error": "SERPAPI_API_KEY not set."}]

    params = {
        "engine": "google_news",
        "q": query,
        "api_key": api_key,
        "num": max_results,
    }

    try:
        r = requests.get("https://serpapi.com/search", params=params, timeout=20)
        if r.status_code == 401:
            return [{"error": "Invalid SerpAPI key."}]
        r.raise_for_status()

        results = r.json().get("news_results", [])
        if not results:
            return []

        return [
            {
                "title": item.get("title"),
                "content": item.get("snippet"),
                "source": item.get("link"),
            }
            for item in results
        ]
    except requests.exceptions.RequestException as e:
        return [{"error": f"SerpAPI error: {str(e)}"}]


@tool("search_news_tavily")
def search_news_tavily(query: str, max_results: int = 5) -> List[Dict]:
    """Search recent financial news using Tavily."""
    results = _tavily_search_logic(query, max_results)
    if not results:
        return [{"info": f"No news results found for query: {query}"}]
    return results


@tool("search_news_serpapi")
def search_news_serpapi(query: str, max_results: int = 5) -> List[Dict]:
    """Search recent financial news using SerpAPI (Google News)."""
    results = _serpapi_search_logic(query, max_results)
    if not results:
        return [{"info": f"No news results found for query: {query}"}]
    return results


@tool("search_news_combined")
def search_news_combined(query: str, max_results: int = 5) -> List[Dict]:
    """
    Search for news using Tavily first, then SerpAPI as fallback.
    Recommended tool - automatically handles failures.
    """
    # 1. Try Tavily
    tavily_results = _tavily_search_logic(query, max_results)

    # Check validity (list is not empty and has no errors)
    if tavily_results and not any("error" in r for r in tavily_results):
        return tavily_results

    # 2. Fallback to SerpAPI
    serpapi_results = _serpapi_search_logic(query, max_results)

    if serpapi_results and not any("error" in r for r in serpapi_results):
        return serpapi_results

    # 3. Both failed
    return [
        {
            "title": "No news available",
            "content": f"Unable to retrieve news for: {query}. Both sources failed.",
            "source": "none",
            "_is_fallback": True,
        }
    ]
