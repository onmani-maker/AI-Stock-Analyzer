"""Utilities for analyzing U.S. equity price data."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
import yfinance as yf


@dataclass(frozen=True)
class StockSummary:
    """High-level summary statistics for a stock."""

    ticker: str
    latest_close: float
    period_return: float
    average_volume: float
    observations: int


def fetch_stock_history(ticker: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
    """Fetch historical price data for a U.S. stock ticker."""
    symbol = ticker.strip().upper()
    if not symbol:
        raise ValueError("Ticker symbol must not be empty.")

    data = yf.download(symbol, period=period, interval=interval, progress=False)
    if data.empty:
        raise ValueError(f"No price history returned for ticker: {symbol}")

    data.index.name = "date"
    return data


def summarize_stock(ticker: str, history: pd.DataFrame) -> StockSummary:
    """Create a compact summary from historical stock data."""
    if history.empty:
        raise ValueError("History must contain at least one row.")

    close = history["Close"].dropna()
    volume = history["Volume"].dropna()
    if close.empty:
        raise ValueError("History must contain closing prices.")

    latest_close = float(close.iloc[-1])
    first_close = float(close.iloc[0])
    period_return = (latest_close / first_close) - 1 if first_close else 0.0
    average_volume = float(volume.mean()) if not volume.empty else 0.0

    return StockSummary(
        ticker=ticker.strip().upper(),
        latest_close=latest_close,
        period_return=period_return,
        average_volume=average_volume,
        observations=len(history),
    )
