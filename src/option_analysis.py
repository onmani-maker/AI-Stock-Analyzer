"""Options analysis helpers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import yfinance as yf

from utils import DATA_DIR


@dataclass(frozen=True)
class OptionChainSummary:
    """Summary of available option chain liquidity."""

    ticker: str
    expiration: str
    call_contracts: int
    put_contracts: int
    total_open_interest: float


@dataclass(frozen=True)
class DownloadedOptionChain:
    """Downloaded option chain metadata and saved CSV paths."""

    ticker: str
    expiration: str
    available_expirations: tuple[str, ...]
    calls_path: Path
    puts_path: Path
    calls: pd.DataFrame
    puts: pd.DataFrame


DISPLAY_COLUMNS = {
    "strike": "Strike",
    "bid": "Bid",
    "ask": "Ask",
    "lastPrice": "Last Price",
    "volume": "Volume",
    "openInterest": "Open Interest",
    "impliedVolatility": "Implied Volatility",
}


def _normalize_ticker(ticker: str) -> str:
    """Normalize and validate a ticker symbol."""
    symbol = ticker.strip().upper()
    if not symbol:
        raise ValueError("Ticker symbol must not be empty.")
    return symbol


def _normalize_expiration(expiration: str | None, expirations: list[str], ticker: str) -> str:
    """Validate an optional expiration date against the dates returned by yfinance."""
    if not expirations:
        raise ValueError(f"No option expirations available for ticker: {ticker}")

    selected_expiration = expiration or expirations[0]
    if selected_expiration not in expirations:
        available = ", ".join(expirations)
        raise ValueError(
            f"Expiration {selected_expiration} is not available for {ticker}. "
            f"Available expirations: {available}"
        )
    return selected_expiration


def _option_chain_path(ticker: str, expiration: str, contract_type: str) -> Path:
    """Build the CSV path for a saved option chain contract type."""
    safe_expiration = expiration.replace("/", "-").replace(" ", "_")
    return DATA_DIR / "options" / f"{ticker}_{safe_expiration}_{contract_type}.csv"


def list_option_expirations(ticker: str) -> list[str]:
    """List all option expiration dates available from yfinance for a ticker."""
    symbol = _normalize_ticker(ticker)
    stock = yf.Ticker(symbol)
    expirations = list(stock.options)
    if not expirations:
        raise ValueError(f"No option expirations available for ticker: {symbol}")
    return expirations


def fetch_option_chain(ticker: str, expiration: str | None = None) -> tuple[pd.DataFrame, pd.DataFrame, str]:
    """Fetch calls and puts for a ticker and expiration date.

    If ``expiration`` is omitted, the earliest available expiration returned by
    yfinance is selected. Use :func:`list_option_expirations` to display the
    available dates before choosing one.
    """
    symbol = _normalize_ticker(ticker)

    stock = yf.Ticker(symbol)
    expirations = list(stock.options)
    selected_expiration = _normalize_expiration(expiration, expirations, symbol)

    chain = stock.option_chain(selected_expiration)
    return chain.calls, chain.puts, selected_expiration


def format_option_chain_for_display(chain: pd.DataFrame) -> pd.DataFrame:
    """Return option chain columns requested for user-facing display."""
    missing_columns = [column for column in DISPLAY_COLUMNS if column not in chain.columns]
    if missing_columns:
        missing = ", ".join(missing_columns)
        raise ValueError(f"Option chain is missing expected columns: {missing}")

    display_chain = chain[list(DISPLAY_COLUMNS)].rename(columns=DISPLAY_COLUMNS)
    return display_chain.sort_values("Strike").reset_index(drop=True)


def download_option_chain(ticker: str, expiration: str | None = None) -> DownloadedOptionChain:
    """Download calls and puts from yfinance and save them under data/options/.

    Args:
        ticker: Stock ticker symbol to download, such as ``"AAPL"``.
        expiration: Optional expiration date in ``YYYY-MM-DD`` format. When not
            provided, the earliest available expiration is selected.

    Returns:
        Metadata containing available expirations, selected expiration, saved
        CSV paths, and display-ready calls and puts DataFrames.
    """
    symbol = _normalize_ticker(ticker)
    stock = yf.Ticker(symbol)
    expirations = list(stock.options)
    selected_expiration = _normalize_expiration(expiration, expirations, symbol)

    chain = stock.option_chain(selected_expiration)
    calls = format_option_chain_for_display(chain.calls)
    puts = format_option_chain_for_display(chain.puts)

    calls_path = _option_chain_path(symbol, selected_expiration, "calls")
    puts_path = _option_chain_path(symbol, selected_expiration, "puts")
    calls_path.parent.mkdir(parents=True, exist_ok=True)
    calls.to_csv(calls_path, index=False)
    puts.to_csv(puts_path, index=False)

    return DownloadedOptionChain(
        ticker=symbol,
        expiration=selected_expiration,
        available_expirations=tuple(expirations),
        calls_path=calls_path,
        puts_path=puts_path,
        calls=calls,
        puts=puts,
    )


def summarize_option_chain(
    ticker: str,
    calls: pd.DataFrame,
    puts: pd.DataFrame,
    expiration: str,
) -> OptionChainSummary:
    """Summarize call and put contract counts and open interest."""
    call_open_interest = (
        calls.get("openInterest", calls.get("Open Interest", pd.Series(dtype=float))).fillna(0).sum()
    )
    put_open_interest = (
        puts.get("openInterest", puts.get("Open Interest", pd.Series(dtype=float))).fillna(0).sum()
    )

    return OptionChainSummary(
        ticker=ticker.strip().upper(),
        expiration=expiration,
        call_contracts=len(calls),
        put_contracts=len(puts),
        total_open_interest=float(call_open_interest + put_open_interest),
    )
