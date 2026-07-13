"""Command-line entry point for AI Stock Analyzer."""

from __future__ import annotations

import argparse

from option_analysis import download_option_chain, list_option_expirations
from stock_analysis import analyze_stock, format_indicator_table
from utils import ensure_project_directories, format_percentage


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line argument parser."""
    parser = argparse.ArgumentParser(description="Analyze a U.S. stock ticker.")
    parser.add_argument("--ticker", default="AAPL", help="Ticker symbol to analyze.")
    parser.add_argument("--period", default="1y", help="Historical period to fetch.")
    parser.add_argument("--interval", default="1d", help="Historical interval to fetch.")
    parser.add_argument("--options", action="store_true", help="Download and display the selected options chain.")
    parser.add_argument("--expiration", help="Option expiration date to download, such as 2026-01-16.")
    return parser


def main() -> None:
    """Run a basic stock analysis workflow."""
    args = build_parser().parse_args()
    ensure_project_directories()

    summary, enriched_history = analyze_stock(args.ticker, period=args.period, interval=args.interval)

    print(f"Ticker: {summary.ticker}")
    print(f"Latest close: ${summary.latest_close:,.2f}")
    print(f"Period return: {format_percentage(summary.period_return)}")
    print(f"Average volume: {summary.average_volume:,.0f}")
    print(f"Observations: {summary.observations}")
    print("\nLatest technical indicators:")
    print(format_indicator_table(enriched_history))

    if args.options:
        expirations = list_option_expirations(args.ticker)
        print("\nAvailable option expirations:")
        print("\n".join(expirations))

        downloaded_chain = download_option_chain(args.ticker, expiration=args.expiration)
        print(f"\nDownloaded options for {downloaded_chain.ticker} expiring {downloaded_chain.expiration}")
        print(f"Calls saved to: {downloaded_chain.calls_path}")
        print(f"Puts saved to: {downloaded_chain.puts_path}")
        print("\nCalls:")
        print(downloaded_chain.calls.to_string(index=False))
        print("\nPuts:")
        print(downloaded_chain.puts.to_string(index=False))


if __name__ == "__main__":
    main()
