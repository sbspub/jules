import pytest
from shargent.zerodha_trading.zerodha_client import ZerodhaClient

def test_zerodha_client_mock_flow():
    client = ZerodhaClient(api_key="mock", access_token="mock")

    profile = client.get_profile()
    assert profile["broker"] == "ZERODHA"

    margins = client.get_margins()
    assert margins["equity"]["net"] == 100000.0

    quotes = client.get_quote(["RELIANCE"])
    assert "NSE:RELIANCE" in quotes

    sbin_quotes = client.get_quote(["SBIN"])
    assert "NSE:SBIN" in sbin_quotes
    sbin_ohlc = sbin_quotes["NSE:SBIN"]["ohlc"]
    assert "open" in sbin_ohlc
    assert "high" in sbin_ohlc
    assert "low" in sbin_ohlc
    assert "close" in sbin_ohlc
    assert sbin_quotes["NSE:SBIN"]["last_price"] == 800.0

    order = client.place_order(symbol="RELIANCE", transaction_type="BUY", quantity=5, product="MIS")
    assert order["status"] == "SUCCESS"

    orders = client.get_orders()
    assert len(orders) == 1

    cancel_res = client.cancel_order(order["order_id"])
    assert cancel_res["status"] == "SUCCESS"
