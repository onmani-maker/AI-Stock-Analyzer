"""Utilities for analyzing U.S. equity price data."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import yfinance as yf

from indicators import add_technical_indicators
from utils import DATA_DIR, save_dataframe


@dataclass(frozen=True)
class StockSummary:
    """High-level summary statistics for a stock."""

    ticker: str
    latest_close: float
    period_return: float
    average_volume: float
    observations: int


INDICATOR_LABELS = {
    "sma_20": "SMA (20)",
    "sma_50": "SMA (50)",
    "ema_20": "EMA (20)",
    "rsi_14": "RSI (14)",
    "macd": "MACD",
    "macd_signal": "MACD Signal",
    "macd_histogram": "MACD Histogram",
    "bb_upper": "Bollinger Upper (20, 2)",
    "bb_middle": "Bollinger Middle (20)",
    "bb_lower": "Bollinger Lower (20, 2)",
}


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


def analyze_stock(ticker: str, period: str = "1y", interval: str = "1d") -> tuple[StockSummary, pd.DataFrame]:
    """Fetch stock history, append indicators, and return summary plus enriched data."""
    symbol = _normalize_ticker(ticker)
    history = fetch_stock_history(symbol, period=period, interval=interval)
    enriched_history = add_technical_indicators(history)
    summary = summarize_stock(symbol, enriched_history)

    return summary, enriched_history


def latest_indicator_values(history: pd.DataFrame) -> pd.DataFrame:
    """Return the most recent available values for supported indicators."""
    if history.empty:
        raise ValueError("History must contain at least one row.")

    indicator_columns = [column for column in INDICATOR_LABELS if column in history.columns]
    if not indicator_columns:
        history = add_technical_indicators(history)
        indicator_columns = [column for column in INDICATOR_LABELS if column in history.columns]

    latest_values = history[indicator_columns].ffill().iloc[-1]
    rows = [
        {
            "Indicator": INDICATOR_LABELS[column],
            "Value": latest_values[column],
        }
        for column in indicator_columns
    ]

    return pd.DataFrame(rows)


def format_indicator_table(history: pd.DataFrame) -> str:
    """Format the latest indicator values as a clean text table."""
    indicators = latest_indicator_values(history).copy()
    indicators["Value"] = indicators["Value"].map(
        lambda value: "N/A" if pd.isna(value) else f"{float(value):,.2f}"
    )

    return indicators.to_string(index=False)
