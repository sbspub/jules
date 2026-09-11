import sys
import os
import io
import contextlib
import pytest
from unittest.mock import patch

from shargent.main import main


LIVE_SBIN_QUOTE = {
    "NSE:SBIN": {
        "last_price": 800.0,
        "ohlc": {"open": 792.0, "high": 816.0, "low": 784.0, "close": 796.0},
        "volume": 500000,
    }
}

def test_main_with_sbin_positional(capsys):
    test_args = ["main.py", "SBIN"]
    with patch.object(sys, "argv", test_args), patch(
        "shargent.zerodha_trading.zerodha_client.ZerodhaClient.get_quote", return_value=LIVE_SBIN_QUOTE
    ), patch(
        "shargent.zerodha_trading.zerodha_client.ZerodhaClient.get_daily_history", return_value=[]
    ), patch("shargent.orchestrator.graph.fetch_news", return_value=[]), patch(
        "shargent.orchestrator.graph.fetch_fundamentals", return_value={}
    ):
        main()
    captured = capsys.readouterr().out
    assert "Target Symbol : SBIN" in captured
    assert "MARKET QUOTE / DAY'S OHLC:" in captured
    assert "Symbol    : SBIN" in captured
    assert "Open      : 792.0" in captured
    assert "High      : 816.0" in captured
    assert "Low       : 784.0" in captured
    assert "Close     : 796.0" in captured

def test_main_with_symbol_flag(capsys):
    test_args = ["main.py", "--symbol", "SBIN"]
    with patch.object(sys, "argv", test_args), patch(
        "shargent.zerodha_trading.zerodha_client.ZerodhaClient.get_quote", return_value=LIVE_SBIN_QUOTE
    ), patch(
        "shargent.zerodha_trading.zerodha_client.ZerodhaClient.get_daily_history", return_value=[]
    ), patch("shargent.orchestrator.graph.fetch_news", return_value=[]), patch(
        "shargent.orchestrator.graph.fetch_fundamentals", return_value={}
    ):
        main()
    captured = capsys.readouterr().out
    assert "Target Symbol : SBIN" in captured
    assert "Open      : 792.0" in captured

def test_main_with_ticker_flag(capsys):
    test_args = ["main.py", "-t", "SBIN"]
    with patch.object(sys, "argv", test_args), patch(
        "shargent.zerodha_trading.zerodha_client.ZerodhaClient.get_quote", return_value=LIVE_SBIN_QUOTE
    ), patch(
        "shargent.zerodha_trading.zerodha_client.ZerodhaClient.get_daily_history", return_value=[]
    ), patch("shargent.orchestrator.graph.fetch_news", return_value=[]), patch(
        "shargent.orchestrator.graph.fetch_fundamentals", return_value={}
    ):
        main()
    captured = capsys.readouterr().out
    assert "Target Symbol : SBIN" in captured
    assert "Open      : 792.0" in captured
