import pytest
from shargent.news_analyser.analyser import NewsAnalyser

def test_news_analyser_empty():
    analyser = NewsAnalyser()
    res = analyser.analyze("RELIANCE", [])
    assert res.overall_sentiment == "NEUTRAL"
    assert res.sentiment_score == 0.0
    assert res.trading_recommendation == "HOLD"

def test_news_analyser_heuristic_positive():
    analyser = NewsAnalyser(api_key="mock_key")
    news = [
        {"title": "RELIANCE reports record profit and high growth in Q3", "snippet": "Massive earnings surge beat expectations."}
    ]
    res = analyser.analyze("RELIANCE", news)
    assert res.overall_sentiment == "BULLISH"
    assert res.sentiment_score > 0
    assert res.trading_recommendation == "BUY"

def test_news_analyser_heuristic_negative():
    analyser = NewsAnalyser(api_key="mock_key")
    news = [
        {"title": "Regulatory probe and penalty on company following profit drop", "snippet": "Bearish downgrade by analysts."}
    ]
    res = analyser.analyze("RELIANCE", news)
    assert res.overall_sentiment == "BEARISH"
    assert res.sentiment_score < 0
    assert res.trading_recommendation == "SELL"
