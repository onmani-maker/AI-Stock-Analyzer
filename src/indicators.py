"""Technical indicator calculations for market analysis."""

from __future__ import annotations

import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import MACD, SMAIndicator
from ta.volatility import BollingerBands


def add_technical_indicators(history: pd.DataFrame) -> pd.DataFrame:
    """Return price history with common technical indicators appended."""
    if history.empty:
        raise ValueError("History must contain at least one row.")
    if "Close" not in history.columns:
        raise ValueError("History must include a Close column.")

    enriched = history.copy()
    close = enriched["Close"]

    enriched["sma_20"] = SMAIndicator(close=close, window=20).sma_indicator()
    enriched["sma_50"] = SMAIndicator(close=close, window=50).sma_indicator()
    enriched["rsi_14"] = RSIIndicator(close=close, window=14).rsi()

    macd = MACD(close=close)
    enriched["macd"] = macd.macd()
    enriched["macd_signal"] = macd.macd_signal()
    enriched["macd_diff"] = macd.macd_diff()

    bands = BollingerBands(close=close)
    enriched["bb_high"] = bands.bollinger_hband()
    enriched["bb_low"] = bands.bollinger_lband()
    enriched["bb_mid"] = bands.bollinger_mavg()

    return enriched
