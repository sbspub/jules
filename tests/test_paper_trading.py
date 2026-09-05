import pytest
from shargent.paper_trading.paper_engine import PaperEngine, LearningMode

def test_paper_engine_trades():
    engine = PaperEngine(initial_balance=100000.0)

    # Buy 10 shares @ 100
    res1 = engine.execute_paper_trade(symbol="RELIANCE", action="BUY", quantity=10, price=100.0)
    assert res1["status"] == "SUCCESS"
    assert engine.balance == 99000.0
    assert "RELIANCE" in engine.positions

    # Sell 10 shares @ 120 (gain 200)
    res2 = engine.execute_paper_trade(symbol="RELIANCE", action="SELL", quantity=10, price=120.0)
    assert res2["status"] == "SUCCESS"
    assert res2["realized_pnl"] == 200.0
    assert engine.balance == 100200.0
    assert "RELIANCE" not in engine.positions

    summary = engine.get_portfolio_summary()
    assert summary["realized_pnl"] == 200.0

def test_learning_mode():
    engine = PaperEngine(initial_balance=100000.0)
    engine.execute_paper_trade(symbol="TCS", action="BUY", quantity=10, price=1000.0)
    engine.execute_paper_trade(symbol="TCS", action="SELL", quantity=10, price=1100.0)

    learning = LearningMode(engine)
    perf = learning.evaluate_performance()
    # 2 total trades recorded: BUY (pnl 0) and SELL (pnl +1000).
    # 1 out of 2 trades has realized_pnl > 0 => win rate 50%.
    assert perf["total_trades"] == 2
    assert perf["total_realized_profit"] == 1000.0
