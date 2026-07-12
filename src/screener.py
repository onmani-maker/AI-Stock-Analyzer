"""Simple stock screening utilities."""

from __future__ import annotations

from collections.abc import Iterable

import pandas as pd

from stock_analysis import fetch_stock_history, summarize_stock


def screen_by_return(tickers: Iterable[str], minimum_return: float = 0.05) -> pd.DataFrame:
    """Screen tickers by period return over the default historical window."""
    rows: list[dict[str, float | int | str]] = []

    for ticker in tickers:
        history = fetch_stock_history(ticker)
        summary = summarize_stock(ticker, history)
        if summary.period_return >= minimum_return:
            rows.append(
                {
                    "ticker": summary.ticker,
                    "latest_close": summary.latest_close,
                    "period_return": summary.period_return,
                    "average_volume": summary.average_volume,
                    "observations": summary.observations,
                }
            )

    return pd.DataFrame(rows).sort_values("period_return", ascending=False, ignore_index=True)
