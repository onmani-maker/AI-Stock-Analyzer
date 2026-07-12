"""Utilities for analyzing U.S. equity price data."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import yfinance as yf

from utils import DATA_DIR, save_dataframe


@dataclass(frozen=True)
class StockSummary:
    """High-level summary statistics for a stock."""

    ticker: str
    latest_close: float
    period_return: float
    average_volume: float
    observations: int


def _normalize_ticker(ticker: str) -> str:
    """Normalize and validate a ticker symbol."""
    symbol = ticker.strip().upper()
    if not symbol:
        raise ValueError("Ticker symbol must not be empty.")
    return symbol


def _stock_data_path(ticker: str, period: str, interval: str) -> Path:
    """Build the CSV path for downloaded stock data."""
    safe_period = period.replace("/", "-").replace(" ", "_")
    safe_interval = interval.replace("/", "-").replace(" ", "_")
    return DATA_DIR / "stocks" / f"{ticker}_{safe_period}_{safe_interval}.csv"


def fetch_stock_history(ticker: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
    """Fetch historical price data for a U.S. stock ticker."""
    symbol = _normalize_ticker(ticker)

    try:
        data = yf.download(symbol, period=period, interval=interval, progress=False)
    except Exception as exc:  # yfinance can raise several network/provider exceptions.
        raise RuntimeError(f"Failed to download price history for ticker: {symbol}") from exc

    if data.empty:
        raise ValueError(f"No price history returned for ticker: {symbol}")

    data.index.name = "date"
    return data


def download_stock_data(ticker: str, period: str = "1y", interval: str = "1d") -> Path:
    """Download historical stock data and save it as a CSV under data/stocks/.

    Args:
        ticker: Stock ticker symbol to download, such as ``"AAPL"``.
        period: yfinance history period, such as ``"1mo"`` or ``"1y"``.
        interval: yfinance data interval, such as ``"1d"`` or ``"1h"``.

    Returns:
        Path to the CSV file containing the downloaded historical data.

    Raises:
        ValueError: If the ticker is empty or yfinance returns no rows.
        RuntimeError: If the yfinance request or CSV write fails.
    """
    symbol = _normalize_ticker(ticker)
    data = fetch_stock_history(symbol, period=period, interval=interval)
    path = _stock_data_path(symbol, period, interval)

    try:
        save_dataframe(data, path)
    except Exception as exc:
        raise RuntimeError(f"Failed to save stock data for ticker {symbol} to {path}") from exc

    return path


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
