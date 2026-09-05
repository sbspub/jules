import pytest
from shargent.technical_analyser.analyser import TechnicalAnalyser

def test_technical_analyser_empty():
    analyser = TechnicalAnalyser()
    res = analyser.analyze("INFY", [])
    assert res.current_price == 100.0
    assert res.trend == "SIDEWAYS"

def test_technical_analyser_uptrend():
    analyser = TechnicalAnalyser()
    price_history = [
        {"close": 100.0 + i, "high": 101.0 + i, "low": 99.0 + i, "volume": 1000}
        for i in range(60)
    ]
    res = analyser.analyze("INFY", price_history)
    assert res.trend == "UPTREND"
    assert res.long_term_signal == "BUY"
