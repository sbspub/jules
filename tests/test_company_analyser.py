import pytest
from shargent.company_analyser.analyser import CompanyAnalyser

def test_company_analyser_strong():
    analyser = CompanyAnalyser()
    financials = {
        "pe_ratio": 18.0,
        "debt_to_equity": 0.2,
        "roe_pct": 22.0,
        "revenue_growth_yo_y": 20.0
    }
    res = analyser.analyze("TCS", financials)
    assert res.financial_health == "STRONG"
    assert res.fundamental_score >= 70
    assert res.long_term_outlook == "BULLISH"

def test_company_analyser_weak():
    analyser = CompanyAnalyser()
    financials = {
        "pe_ratio": 75.0,
        "debt_to_equity": 2.1,
        "roe_pct": 4.0,
        "revenue_growth_yo_y": -5.0
    }
    res = analyser.analyze("WEAKCO", financials)
    assert res.financial_health == "WEAK"
    assert res.fundamental_score < 45
    assert res.long_term_outlook == "BEARISH"
