import pytest
from shargent.orchestrator.graph import TradingOrchestrator
from shargent.zerodha_trading.zerodha_client import ZerodhaClient

def test_orchestrator_auto_day_trade():
    orchestrator = TradingOrchestrator(zerodha_client=ZerodhaClient(api_key="mock", access_token="mock"))
    res = orchestrator.run_strategy(
        symbol="RELIANCE",
        strategy_mode="AUTO_DAY_TRADE",
        trading_mode="PAPER",
        quantity=5
    )

    assert res["symbol"] == "RELIANCE"
    assert res["final_decision"] in ["BUY", "SELL", "HOLD"]
    assert res["execution_result"] is not None

def test_orchestrator_long_term_investment():
    orchestrator = TradingOrchestrator(zerodha_client=ZerodhaClient(api_key="mock", access_token="mock"))
    res = orchestrator.run_strategy(
        symbol="TCS",
        strategy_mode="LONG_TERM_INVESTMENT",
        trading_mode="PAPER",
        quantity=10
    )

    assert res["symbol"] == "TCS"
    assert res["company_result"] is not None
    assert res["final_decision"] in ["BUY", "SELL", "HOLD"]
