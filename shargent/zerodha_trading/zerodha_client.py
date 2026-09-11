from typing import Dict, Any, List, Optional
import os
import random
import logging
from datetime import date, timedelta

logger = logging.getLogger(__name__)


class ZerodhaQuoteError(RuntimeError):
    """Raised when a quote cannot be obtained from the Zerodha Kite API."""


class ZerodhaClient:
    def __init__(self, api_key: Optional[str] = None, access_token: Optional[str] = None):
        self.api_key = api_key or os.getenv("ZERODHA_API_KEY", "")
        self.access_token = access_token or os.getenv("ZERODHA_ACCESS_TOKEN", "")
        self.is_live = bool(self.api_key and self.access_token and not self.api_key.startswith("mock"))

        self.kite = None
        if self.is_live:
            try:
                from kiteconnect import KiteConnect
                self.kite = KiteConnect(api_key=self.api_key)
                self.kite.set_access_token(self.access_token)
            except Exception as e:
                logger.warning(f"Could not initialize KiteConnect client: {e}. Live quote requests will fail.")
                self.is_live = False

        # Internal state for mock mode
        self._mock_orders = {}
        self._order_counter = 1000

    def get_profile(self) -> Dict[str, Any]:
        """Fetches user profile information."""
        if self.is_live and self.kite:
            try:
                return self.kite.profile()
            except Exception as e:
                logger.error(f"Error fetching Zerodha profile: {e}")

        return {
            "user_id": "SHARGENT_USER",
            "user_name": "Zerodha Trader",
            "email": "trader@shargent.local",
            "user_type": "individual",
            "broker": "ZERODHA"
        }

    def get_margins(self) -> Dict[str, Any]:
        """Fetches account balance and margin details."""
        if self.is_live and self.kite:
            try:
                return self.kite.margins()
            except Exception as e:
                logger.error(f"Error fetching Zerodha margins: {e}")

        return {
            "equity": {
                "enabled": True,
                "net": 100000.0,
                "available": {
                    "cash": 85000.0,
                    "opening_balance": 100000.0,
                    "live_balance": 85000.0,
                    "collateral": 0.0
                },
                "utilised": {
                    "debits": 15000.0,
                    "exposure": 0.0,
                    "span": 0.0
                }
            }
        }

    def get_quote(self, symbols: List[str]) -> Dict[str, Any]:
        """Fetch Kite quotes, or fixtures for an explicitly constructed mock client.

        Normal clients never substitute a made-up quote for a failed live request.
        """
        formatted_symbols = [s if ":" in s else f"NSE:{s}" for s in symbols]
        if self.is_live and self.kite:
            try:
                return self.kite.quote(formatted_symbols)
            except Exception as e:
                raise ZerodhaQuoteError(f"Zerodha Kite quote request failed: {e}") from e

        if not self.api_key or not self.access_token:
            raise ZerodhaQuoteError(
                "Zerodha credentials are not configured. Set ZERODHA_API_KEY and "
                "a current ZERODHA_ACCESS_TOKEN before requesting market data."
            )

        if not self.api_key.startswith("mock"):
            raise ZerodhaQuoteError(
                "KiteConnect could not be initialized. Install/configure kiteconnect "
                "and verify ZERODHA_API_KEY and ZERODHA_ACCESS_TOKEN."
            )

        # Fixtures are available only to callers that deliberately construct a
        # mock client (api_key="mock"), such as isolated unit tests.
        mock_prices = {
            "RELIANCE": 2500.0,
            "TCS": 3500.0,
            "SBIN": 800.0,
            "INFY": 1800.0,
            "INFYS": 1800.0,
            "HDFCBANK": 1600.0,
            "ICICIBANK": 1000.0,
        }

        quotes = {}
        for s in formatted_symbols:
            clean_sym = s.split(":")[-1].upper()
            base_price = mock_prices.get(clean_sym, 1500.0)
            quotes[s] = {
                "instrument_token": random.randint(100000, 999999),
                "timestamp": "2025-01-01T10:00:00",
                "last_price": round(base_price, 2),
                "ohlc": {
                    "open": round(base_price * 0.99, 2),
                    "high": round(base_price * 1.02, 2),
                    "low": round(base_price * 0.98, 2),
                    "close": round(base_price * 0.995, 2)
                },
                "volume": 500000,
                "buy_quantity": 10000,
                "sell_quantity": 8000
            }
        return quotes

    def get_daily_history(self, symbol: str, calendar_days: int = 100) -> List[Dict[str, Any]]:
        """Return actual daily candles for analysis, or explicit test fixtures."""
        if self.is_live and self.kite:
            try:
                quote = self.get_quote([symbol])
                key = symbol if ":" in symbol else f"NSE:{symbol}"
                data = quote.get(key) or next(iter(quote.values()))
                instrument_token = data.get("instrument_token")
                if not instrument_token:
                    raise ZerodhaQuoteError(f"Kite did not return an instrument token for {symbol}")
                candles = self.kite.historical_data(
                    instrument_token,
                    date.today() - timedelta(days=calendar_days),
                    date.today(),
                    "day",
                )
                if len(candles) < 30:
                    raise ZerodhaQuoteError(f"Kite returned only {len(candles)} daily candles for {symbol}")
                return candles
            except ZerodhaQuoteError:
                raise
            except Exception as exc:
                raise ZerodhaQuoteError(f"Zerodha Kite historical-data request failed: {exc}") from exc

        if self.api_key.startswith("mock"):
            base_price = self.get_quote([symbol])[f"NSE:{symbol.split(':')[-1]}"]["last_price"]
            return [
                {"close": base_price, "high": base_price * 1.01, "low": base_price * 0.99, "volume": 1000}
                for _ in range(30)
            ]
        raise ZerodhaQuoteError("Live Zerodha credentials are required for real historical analysis.")

    def place_order(
        self,
        symbol: str,
        transaction_type: str,  # BUY or SELL
        quantity: int,
        order_type: str = "MARKET",  # MARKET or LIMIT
        price: float = 0.0,
        product: str = "MIS",        # MIS (day trade) or CNC (long term delivery)
        exchange: str = "NSE"
    ) -> Dict[str, Any]:
        """Places a buy or sell order via Zerodha Kite or mock execution."""
        clean_symbol = symbol.split(":")[-1]

        if self.is_live and self.kite:
            try:
                order_id = self.kite.place_order(
                    variety=self.kite.VARIETY_REGULAR,
                    exchange=exchange,
                    tradingsymbol=clean_symbol,
                    transaction_type=transaction_type,
                    quantity=quantity,
                    product=product,
                    order_type=order_type,
                    price=price if order_type == "LIMIT" else None
                )
                return {
                    "status": "SUCCESS",
                    "order_id": order_id,
                    "message": f"Order placed successfully in Zerodha Live (ID: {order_id})"
                }
            except Exception as e:
                logger.error(f"Zerodha place_order failed: {e}")
                return {"status": "ERROR", "message": str(e)}

        # Mock Order Execution
        self._order_counter += 1
        order_id = f"MOCK_{self._order_counter}"

        order_details = {
            "order_id": order_id,
            "symbol": clean_symbol,
            "exchange": exchange,
            "transaction_type": transaction_type,
            "quantity": quantity,
            "order_type": order_type,
            "price": price,
            "product": product,
            "status": "COMPLETE",
            "message": "Executed in Zerodha Sandbox/Mock environment"
        }
        self._mock_orders[order_id] = order_details

        return {
            "status": "SUCCESS",
            "order_id": order_id,
            "details": order_details
        }

    def cancel_order(self, order_id: str) -> Dict[str, Any]:
        """Cancels an existing pending order."""
        if self.is_live and self.kite:
            try:
                self.kite.cancel_order(variety=self.kite.VARIETY_REGULAR, order_id=order_id)
                return {"status": "SUCCESS", "order_id": order_id, "message": "Order cancelled successfully"}
            except Exception as e:
                return {"status": "ERROR", "message": str(e)}

        if order_id in self._mock_orders:
            self._mock_orders[order_id]["status"] = "CANCELLED"
            return {"status": "SUCCESS", "order_id": order_id, "message": "Mock order cancelled successfully"}

        return {"status": "ERROR", "message": f"Order ID {order_id} not found"}

    def get_orders(self) -> List[Dict[str, Any]]:
        """Retrieves list of orders."""
        if self.is_live and self.kite:
            try:
                return self.kite.orders()
            except Exception as e:
                logger.error(f"Error fetching Zerodha orders: {e}")

        return list(self._mock_orders.values())

    def get_positions(self) -> Dict[str, Any]:
        """Retrieves current open positions."""
        if self.is_live and self.kite:
            try:
                return self.kite.positions()
            except Exception as e:
                logger.error(f"Error fetching Zerodha positions: {e}")

        return {
            "net": [
                {
                    "tradingsymbol": "RELIANCE",
                    "exchange": "NSE",
                    "quantity": 10,
                    "average_price": 2480.0,
                    "last_price": 2510.0,
                    "pnl": 300.0,
                    "product": "MIS"
                }
            ],
            "day": []
        }

    def get_holdings(self) -> List[Dict[str, Any]]:
        """Retrieves long term CNC portfolio holdings."""
        if self.is_live and self.kite:
            try:
                return self.kite.holdings()
            except Exception as e:
                logger.error(f"Error fetching Zerodha holdings: {e}")

        return [
            {
                "tradingsymbol": "TCS",
                "exchange": "NSE",
                "quantity": 25,
                "average_price": 3200.0,
                "last_price": 3550.0,
                "pnl": 8750.0,
                "product": "CNC"
            }
        ]
