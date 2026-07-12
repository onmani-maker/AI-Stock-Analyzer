"""Options analysis helpers."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
import yfinance as yf


@dataclass(frozen=True)
class OptionChainSummary:
    """Summary of available option chain liquidity."""

    ticker: str
    expiration: str
    call_contracts: int
    put_contracts: int
    total_open_interest: float


def fetch_option_chain(ticker: str, expiration: str | None = None) -> tuple[pd.DataFrame, pd.DataFrame, str]:
    """Fetch calls and puts for a ticker and expiration date."""
    symbol = ticker.strip().upper()
    if not symbol:
        raise ValueError("Ticker symbol must not be empty.")

    stock = yf.Ticker(symbol)
    expirations = list(stock.options)
    if not expirations:
        raise ValueError(f"No option expirations available for ticker: {symbol}")

    selected_expiration = expiration or expirations[0]
    if selected_expiration not in expirations:
        raise ValueError(f"Expiration {selected_expiration} is not available for {symbol}.")

    chain = stock.option_chain(selected_expiration)
    return chain.calls, chain.puts, selected_expiration


def summarize_option_chain(
    ticker: str,
    calls: pd.DataFrame,
    puts: pd.DataFrame,
    expiration: str,
) -> OptionChainSummary:
    """Summarize call and put contract counts and open interest."""
    call_open_interest = calls.get("openInterest", pd.Series(dtype=float)).fillna(0).sum()
    put_open_interest = puts.get("openInterest", pd.Series(dtype=float)).fillna(0).sum()

    return OptionChainSummary(
        ticker=ticker.strip().upper(),
        expiration=expiration,
        call_contracts=len(calls),
        put_contracts=len(puts),
        total_open_interest=float(call_open_interest + put_open_interest),
    )
