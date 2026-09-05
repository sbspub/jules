from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import os
import json

class NewsAnalysisResult(BaseModel):
    symbol: str
    overall_sentiment: str = Field(description="BULLISH, BEARISH, or NEUTRAL")
    sentiment_score: float = Field(description="Score between -1.0 (extremely bearish) and +1.0 (extremely bullish)")
    impact_level: str = Field(description="HIGH, MEDIUM, or LOW")
    key_highlights: List[str] = Field(default_factory=list)
    affected_segments: List[str] = Field(default_factory=list, description="Business, industry, political, macro factors")
    summary: str
    trading_recommendation: str = Field(description="BUY, SELL, or HOLD recommendation based on news")

class NewsAnalyser:
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self.model = model

    def analyze(self, symbol: str, news_items: List[Dict[str, Any]]) -> NewsAnalysisResult:
        """
        Analyzes news articles/headlines for a given symbol.
        Uses OpenAI structured LLM call if API key is valid/configured,
        otherwise provides robust heuristic analysis for local testing.
        """
        if not news_items:
            return NewsAnalysisResult(
                symbol=symbol,
                overall_sentiment="NEUTRAL",
                sentiment_score=0.0,
                impact_level="LOW",
                key_highlights=["No recent news available"],
                affected_segments=[],
                summary=f"No recent news available for {symbol}.",
                trading_recommendation="HOLD"
            )

        # Attempt LLM analysis if API key is provided and not a placeholder
        if self.api_key and not self.api_key.startswith("mock") and len(self.api_key) > 10:
            try:
                from langchain_openai import ChatOpenAI
                from langchain_core.messages import SystemMessage, HumanMessage

                llm = ChatOpenAI(model=self.model, openai_api_key=self.api_key, temperature=0.1)

                news_text = "\n".join([
                    f"- Title: {item.get('title', '')} | Content: {item.get('content', item.get('snippet', ''))} | Source: {item.get('source', '')}"
                    for item in news_items
                ])

                prompt = f"""
                Analyze the following news articles regarding stock '{symbol}'.
                Categorize impact on business, industry, politics, macroeconomics, and share price.

                News items:
                {news_text}

                Return JSON matching this schema:
                {{
                  "overall_sentiment": "BULLISH|BEARISH|NEUTRAL",
                  "sentiment_score": float between -1.0 and 1.0,
                  "impact_level": "HIGH|MEDIUM|LOW",
                  "key_highlights": ["list of key points"],
                  "affected_segments": ["list of segments"],
                  "summary": "brief summary",
                  "trading_recommendation": "BUY|SELL|HOLD"
                }}
                """

                structured_llm = llm.with_structured_output(NewsAnalysisResult)
                res = structured_llm.invoke([
                    SystemMessage(content="You are an expert financial news analyst specializing in Indian stock market (NSE/BSE)."),
                    HumanMessage(content=prompt)
                ])
                res.symbol = symbol
                return res
            except Exception as e:
                # Fallback to heuristic parser if OpenAI API call fails or fails key validation
                pass

        # Heuristic / Rule-based rule parsing for local mode/mock tests
        positive_keywords = ["growth", "profit", "record", "order", "surge", "beat", "expansion", "approval", "dividend", "bullish", "upgrade"]
        negative_keywords = ["loss", "fall", "drop", "probe", "investigation", "penalty", "fraud", "miss", "downgrade", "bearish", "decline", "cut"]

        total_score = 0.0
        highlights = []
        segments = set()

        for item in news_items:
            text = (item.get("title", "") + " " + item.get("content", "") + " " + item.get("snippet", "")).lower()
            pos_count = sum(1 for kw in positive_keywords if kw in text)
            neg_count = sum(1 for kw in negative_keywords if kw in text)

            item_score = (pos_count - neg_count) * 0.25
            total_score += max(-1.0, min(1.0, item_score))

            if item.get("title"):
                highlights.append(item["title"])

            if "govt" in text or "policy" in text or "tax" in text or "election" in text:
                segments.add("Politics & Regulation")
            if "earnings" in text or "q1" in text or "q2" in text or "q3" in text or "q4" in text or "revenue" in text:
                segments.add("Business & Financials")
            if "sector" in text or "industry" in text:
                segments.add("Industry Trends")

        avg_score = total_score / max(1, len(news_items))
        avg_score = max(-1.0, min(1.0, avg_score))

        if avg_score > 0.2:
            sentiment = "BULLISH"
            recommendation = "BUY"
        elif avg_score < -0.2:
            sentiment = "BEARISH"
            recommendation = "SELL"
        else:
            sentiment = "NEUTRAL"
            recommendation = "HOLD"

        abs_score = abs(avg_score)
        impact = "HIGH" if abs_score > 0.5 else ("MEDIUM" if abs_score > 0.2 else "LOW")

        return NewsAnalysisResult(
            symbol=symbol,
            overall_sentiment=sentiment,
            sentiment_score=round(avg_score, 2),
            impact_level=impact,
            key_highlights=highlights[:5] or ["Analyzed news headlines."],
            affected_segments=list(segments) or ["General Market"],
            summary=f"Processed {len(news_items)} news items for {symbol}. Overall sentiment is {sentiment}.",
            trading_recommendation=recommendation
        )
