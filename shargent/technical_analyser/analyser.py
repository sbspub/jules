from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import pandas as pd
import numpy as np

class TechnicalAnalysisResult(BaseModel):
    symbol: str
    current_price: float
    rsi_14: float
    macd_signal: str = Field(description="BULLISH_CROSS, BEARISH_CROSS, or NEUTRAL")
    vwap: float
    sma_50: float
    sma_200: float
    trend: str = Field(description="UPTREND, DOWNTREND, or SIDEWAYS")
    short_term_signal: str = Field(description="BUY, SELL, or HOLD")
    long_term_signal: str = Field(description="BUY, SELL, or HOLD")
    support_level: float
    resistance_level: float
    confidence_score: float = Field(description="0.0 to 1.0 confidence rating")
    indicators_summary: Dict[str, Any]

class TechnicalAnalyser:
    def __init__(self):
        pass

    def compute_rsi(self, series: pd.Series, period: int = 14) -> float:
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / (loss + 1e-9)
        rsi = 100 - (100 / (1 + rs))
        return float(rsi.iloc[-1]) if not rsi.empty and not pd.isna(rsi.iloc[-1]) else 50.0

    def compute_macd(self, series: pd.Series) -> str:
        exp1 = series.ewm(span=12, adjust=False).mean()
        exp2 = series.ewm(span=26, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=9, adjust=False).mean()

        if len(macd) < 2 or len(signal) < 2:
            return "NEUTRAL"

        prev_diff = macd.iloc[-2] - signal.iloc[-2]
        curr_diff = macd.iloc[-1] - signal.iloc[-1]

        if prev_diff <= 0 and curr_diff > 0:
            return "BULLISH_CROSS"
        elif prev_diff >= 0 and curr_diff < 0:
            return "BEARISH_CROSS"
        elif curr_diff > 0:
            return "BULLISH"
        elif curr_diff < 0:
            return "BEARISH"
        return "NEUTRAL"

    def compute_vwap(self, df: pd.DataFrame) -> float:
        if "volume" not in df or "close" not in df or df["volume"].sum() == 0:
            return float(df["close"].iloc[-1]) if "close" in df and not df.empty else 0.0

        typical_price = (df["high"] + df["low"] + df["close"]) / 3.0
        vwap = (typical_price * df["volume"]).sum() / df["volume"].sum()
        return float(vwap)

    def analyze(self, symbol: str, price_history: List[Dict[str, Any]]) -> TechnicalAnalysisResult:
        """
        Calculates short-term and long-term technical indicators and returns trade signals.
        price_history items should be dicts containing: close, high, low, volume (optional: open, date)
        """
        if not price_history:
            # Return neutral fallback
            return TechnicalAnalysisResult(
                symbol=symbol,
                current_price=100.0,
                rsi_14=50.0,
                macd_signal="NEUTRAL",
                vwap=100.0,
                sma_50=100.0,
                sma_200=100.0,
                trend="SIDEWAYS",
                short_term_signal="HOLD",
                long_term_signal="HOLD",
                support_level=95.0,
                resistance_level=105.0,
                confidence_score=0.5,
                indicators_summary={"note": "Empty price history provided"}
            )

        df = pd.DataFrame(price_history)
        if "close" not in df:
            df["close"] = 100.0
        if "high" not in df:
            df["high"] = df["close"] * 1.01
        if "low" not in df:
            df["low"] = df["close"] * 0.99
        if "volume" not in df:
            df["volume"] = 1000

        curr_price = float(df["close"].iloc[-1])
        rsi = self.compute_rsi(df["close"])
        macd_sig = self.compute_macd(df["close"])
        vwap_val = self.compute_vwap(df)

        sma_50 = float(df["close"].rolling(min(50, len(df))).mean().iloc[-1])
        sma_200 = float(df["close"].rolling(min(200, len(df))).mean().iloc[-1])

        support = float(df["low"].min())
        resistance = float(df["high"].max())

        # Trend Determination
        if curr_price > sma_50 and sma_50 >= sma_200:
            trend = "UPTREND"
        elif curr_price < sma_50 and sma_50 <= sma_200:
            trend = "DOWNTREND"
        else:
            trend = "SIDEWAYS"

        # Short Term Signal Logic (RSI, VWAP, MACD)
        st_bullish_points = 0
        st_bearish_points = 0

        if rsi < 35:
            st_bullish_points += 2  # Oversold
        elif rsi > 65:
            st_bearish_points += 2  # Overbought

        if curr_price > vwap_val:
            st_bullish_points += 1
        else:
            st_bearish_points += 1

        if macd_sig in ["BULLISH_CROSS", "BULLISH"]:
            st_bullish_points += 2
        elif macd_sig in ["BEARISH_CROSS", "BEARISH"]:
            st_bearish_points += 2

        if st_bullish_points >= 3 and st_bullish_points > st_bearish_points:
            short_signal = "BUY"
        elif st_bearish_points >= 3 and st_bearish_points > st_bullish_points:
            short_signal = "SELL"
        else:
            short_signal = "HOLD"

        # Long Term Signal Logic (50/200 SMA, Trend, Major Support)
        if trend == "UPTREND" and curr_price > sma_200:
            long_signal = "BUY"
        elif trend == "DOWNTREND" or curr_price < sma_200 * 0.95:
            long_signal = "SELL"
        else:
            long_signal = "HOLD"

        confidence = round(min(1.0, max(0.4, abs(st_bullish_points - st_bearish_points) / 5.0 + 0.3)), 2)

        return TechnicalAnalysisResult(
            symbol=symbol,
            current_price=round(curr_price, 2),
            rsi_14=round(rsi, 2),
            macd_signal=macd_sig,
            vwap=round(vwap_val, 2),
            sma_50=round(sma_50, 2),
            sma_200=round(sma_200, 2),
            trend=trend,
            short_term_signal=short_signal,
            long_term_signal=long_signal,
            support_level=round(support, 2),
            resistance_level=round(resistance, 2),
            confidence_score=confidence,
            indicators_summary={
                "rsi_14": round(rsi, 2),
                "macd_signal": macd_sig,
                "vwap": round(vwap_val, 2),
                "sma_50": round(sma_50, 2),
                "sma_200": round(sma_200, 2)
            }
        )
