"""Command-line entry point for AI Stock Analyzer."""

from __future__ import annotations

import argparse

from indicators import add_technical_indicators
from stock_analysis import fetch_stock_history, summarize_stock
from utils import ensure_project_directories, format_percentage


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line argument parser."""
    parser = argparse.ArgumentParser(description="Analyze a U.S. stock ticker.")
    parser.add_argument("--ticker", default="AAPL", help="Ticker symbol to analyze.")
    parser.add_argument("--period", default="1y", help="Historical period to fetch.")
    parser.add_argument("--interval", default="1d", help="Historical interval to fetch.")
    return parser


def main() -> None:
    """Run a basic stock analysis workflow."""
    args = build_parser().parse_args()
    ensure_project_directories()

    history = fetch_stock_history(args.ticker, period=args.period, interval=args.interval)
    enriched_history = add_technical_indicators(history)
    summary = summarize_stock(args.ticker, enriched_history)

    print(f"Ticker: {summary.ticker}")
    print(f"Latest close: ${summary.latest_close:,.2f}")
    print(f"Period return: {format_percentage(summary.period_return)}")
    print(f"Average volume: {summary.average_volume:,.0f}")
    print(f"Observations: {summary.observations}")


if __name__ == "__main__":
    main()
