"""
Researcher Agent - Web & News Scraper
Fetches market news, searches the web for sentiment and risks.
"""

import re
from typing import Dict, Any, List
from openai import OpenAI
from config.settings import get_settings
from utils.api_clients import SearchAPIClient
from utils.formatters import format_news_results
from memory.vector_store import VectorStore


class ResearcherAgent:
    """
    Agent responsible for gathering news and web information about stocks.
    Analyzes sentiment and identifies risks from news sources.
    """

    def __init__(self, vector_store: VectorStore):
        """
        Initialize the Researcher Agent.

        Args:
            vector_store: Shared vector memory for storing findings
        """
        self.settings = get_settings()
        self.client = OpenAI(api_key=self.settings.openai_api_key)
        self.search_client = SearchAPIClient()
        self.vector_store = vector_store
        self.name = "ResearcherAgent"

    def research(self, ticker: str, company_name: str = "") -> Dict[str, Any]:
        """
        Conduct comprehensive research on a ticker.

        Args:
            ticker: Stock ticker symbol
            company_name: Optional company name for better search results

        Returns:
            Dictionary containing research findings
        """
        print(f"[{self.name}] Starting research for {ticker}...")

        # Gather news
        news_articles = self._gather_news(ticker, company_name)

        # Analyze sentiment
        sentiment_analysis = self._analyze_sentiment(ticker, news_articles)

        # Identify risks and opportunities
        risk_analysis = self._identify_risks(ticker, news_articles)

        # Create summary
        summary = self._create_summary(ticker, news_articles, sentiment_analysis, risk_analysis)

        # Store in vector memory
        self._store_findings(ticker, news_articles, sentiment_analysis, risk_analysis, summary)

        findings = {
            'ticker': ticker,
            'news_articles': news_articles,
            'sentiment_analysis': sentiment_analysis,
            'risk_analysis': risk_analysis,
            'summary': summary
        }

        print(f"[{self.name}] Research completed for {ticker}")
        return findings

    def _gather_news(self, ticker: str, company_name: str) -> List[Dict[str, Any]]:
        """Gather recent news articles about the ticker."""
        print(f"[{self.name}] Gathering news for {ticker}...")

        search_query = f"{ticker} {company_name} stock news" if company_name else f"{ticker} stock news"
        news_articles = self.search_client.search_news(search_query, max_results=10)

        return news_articles

    def _analyze_sentiment(self, ticker: str, news_articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze sentiment from news articles using LLM."""
        print(f"[{self.name}] Analyzing sentiment for {ticker}...")

        if not news_articles:
            return {
                'overall_sentiment': 'neutral',
                'sentiment_score': 0,
                'explanation': 'No news articles available for sentiment analysis.'
            }

        # Prepare news context for LLM
        news_context = format_news_results(news_articles)

        prompt = f"""Analyze the sentiment of the following news articles about {ticker}.

News Articles:
{news_context}

Provide:
1. Overall sentiment (bullish/neutral/bearish)
2. Sentiment score (-10 to +10, where -10 is very bearish and +10 is very bullish)
3. Brief explanation (2-3 sentences) of the key factors driving sentiment

Format your response as:
SENTIMENT: [bullish/neutral/bearish]
SCORE: [number]
EXPLANATION: [your explanation]
"""

        try:
            response = self.client.chat.completions.create(
                model=self.settings.openai_model,
                messages=[
                    {"role": "system", "content": "You are a financial analyst specializing in sentiment analysis."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.settings.temperature,
                max_tokens=500
            )

            analysis = response.choices[0].message.content

            print(f"[{self.name}] Raw sentiment analysis response:\n{analysis}")

            # Parse response - more flexible parsing
            sentiment = 'neutral'
            score = 0
            explanation = ''

            # Try to find sentiment
            for keyword in ['SENTIMENT:', 'Sentiment:', 'sentiment:']:
                if keyword in analysis:
                    text_after = analysis.split(keyword, 1)[1].split('\n')[0].strip().lower()
                    if 'bullish' in text_after or 'positive' in text_after:
                        sentiment = 'bullish'
                    elif 'bearish' in text_after or 'negative' in text_after:
                        sentiment = 'bearish'
                    else:
                        sentiment = 'neutral'
                    break

            # Try to find score
            for keyword in ['SCORE:', 'Score:', 'score:']:
                if keyword in analysis:
                    text_after = analysis.split(keyword, 1)[1].split('\n')[0].strip()
                    # Extract first number found
                    numbers = re.findall(r'-?\d+', text_after)
                    if numbers:
                        score = int(numbers[0])
                    break

            # Try to find explanation
            for keyword in ['EXPLANATION:', 'Explanation:', 'explanation:']:
                if keyword in analysis:
                    explanation = analysis.split(keyword, 1)[1].strip()
                    # Take everything after the keyword
                    explanation = explanation.split('\n\n')[0]  # Stop at double newline
                    break

            # If no explanation found, use the whole analysis
            if not explanation:
                explanation = analysis.strip()

            return {
                'overall_sentiment': sentiment,
                'sentiment_score': score,
                'explanation': explanation,
                'raw_analysis': analysis
            }

        except Exception as e:
            print(f"[{self.name}] Error in sentiment analysis: {str(e)}")
            return {
                'overall_sentiment': 'neutral',
                'sentiment_score': 0,
                'explanation': f'Error in analysis: {str(e)}'
            }

    def _identify_risks(self, ticker: str, news_articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Identify risks and opportunities from news."""
        print(f"[{self.name}] Identifying risks for {ticker}...")

        if not news_articles:
            return {
                'risks': [],
                'opportunities': [],
                'summary': 'No news articles available for risk analysis.'
            }

        news_context = format_news_results(news_articles)

        prompt = f"""Based on the following news articles about {ticker}, identify:
1. Key RISKS (potential negative factors)
2. Key OPPORTUNITIES (potential positive factors)

News Articles:
{news_context}

List 3-5 risks and 3-5 opportunities. Be specific and concise.

Format:
RISKS:
- [risk 1]
- [risk 2]
...

OPPORTUNITIES:
- [opportunity 1]
- [opportunity 2]
...
"""

        try:
            response = self.client.chat.completions.create(
                model=self.settings.openai_model,
                messages=[
                    {"role": "system", "content": "You are a financial risk analyst."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.settings.temperature,
                max_tokens=800
            )

            analysis = response.choices[0].message.content

            # Parse risks and opportunities
            risks = []
            opportunities = []
            current_section = None

            for line in analysis.strip().split('\n'):
                line = line.strip()
                if line.startswith('RISKS:'):
                    current_section = 'risks'
                elif line.startswith('OPPORTUNITIES:'):
                    current_section = 'opportunities'
                elif line.startswith('- '):
                    item = line[2:].strip()
                    if current_section == 'risks':
                        risks.append(item)
                    elif current_section == 'opportunities':
                        opportunities.append(item)

            return {
                'risks': risks,
                'opportunities': opportunities,
                'summary': analysis
            }

        except Exception as e:
            print(f"[{self.name}] Error in risk analysis: {str(e)}")
            return {
                'risks': [],
                'opportunities': [],
                'summary': f'Error in analysis: {str(e)}'
            }

    def _create_summary(
        self,
        ticker: str,
        news_articles: List[Dict[str, Any]],
        sentiment: Dict[str, Any],
        risks: Dict[str, Any]
    ) -> str:
        """Create a brief summary of research findings."""
        summary_parts = [
            f"Research Summary for {ticker}:",
            f"- Found {len(news_articles)} recent news articles",
            f"- Overall Sentiment: {sentiment['overall_sentiment'].upper()} (Score: {sentiment['sentiment_score']})",
            f"- Identified {len(risks['risks'])} risks and {len(risks['opportunities'])} opportunities"
        ]

        return "\n".join(summary_parts)

    def _store_findings(
        self,
        ticker: str,
        news_articles: List[Dict[str, Any]],
        sentiment: Dict[str, Any],
        risks: Dict[str, Any],
        summary: str
    ) -> None:
        """Store research findings in vector memory."""
        print(f"[{self.name}] Storing findings in vector memory...")

        # Store summary
        self.vector_store.add_document(
            content=summary,
            metadata={
                'ticker': ticker,
                'agent': self.name,
                'type': 'research_summary'
            }
        )

        # Store sentiment analysis
        self.vector_store.add_document(
            content=f"Sentiment Analysis:\n{sentiment['explanation']}",
            metadata={
                'ticker': ticker,
                'agent': self.name,
                'type': 'sentiment_analysis',
                'sentiment': sentiment['overall_sentiment'],
                'score': sentiment['sentiment_score']
            }
        )

        # Store risks and opportunities
        risks_text = "RISKS:\n" + "\n".join([f"- {r}" for r in risks['risks']])
        opportunities_text = "OPPORTUNITIES:\n" + "\n".join([f"- {o}" for o in risks['opportunities']])

        self.vector_store.add_document(
            content=f"{risks_text}\n\n{opportunities_text}",
            metadata={
                'ticker': ticker,
                'agent': self.name,
                'type': 'risk_analysis'
            }
        )

        # Store individual news articles
        if news_articles:
            contents = []
            metadatas = []

            for article in news_articles[:5]:  # Store top 5 articles
                contents.append(f"{article['title']}\n{article['snippet']}")
                metadatas.append({
                    'ticker': ticker,
                    'agent': self.name,
                    'type': 'news_article',
                    'url': article['url'],
                    'date': article['published_date']
                })

            self.vector_store.add_batch(contents, metadatas)

        print(f"[{self.name}] Findings stored successfully")
