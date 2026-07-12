# AI Stock Analyzer

AI Stock Analyzer is an open-source Python project for analyzing U.S. stocks and options with the help of technical indicators, market screening workflows, and AI-powered reporting.

The project is designed as a clean foundation for research, analytics, and future quantitative trading features.

## Features

- Analyze U.S. equity price history and summary statistics.
- Analyze options chains, including moneyness and basic contract metrics.
- Calculate technical indicators such as moving averages, RSI, MACD, and Bollinger Bands.
- Screen stocks using configurable technical and performance criteria.
- Generate AI-powered market report prompts and summaries.
- Provide an extensible structure for future quantitative trading research.

## Installation

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd AI-Stock-Analyzer
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the example command-line entry point:

```bash
python src/main.py --ticker AAPL
```

Download historical stock data with `yfinance` and save it as a CSV under `data/stocks/`:

```python
from stock_analysis import download_stock_data

csv_path = download_stock_data("AAPL", period="6mo", interval="1d")
print(f"Saved data to {csv_path}")
```

Use the modules in `src/` to fetch stock data, calculate indicators, analyze options, screen tickers, and prepare AI market reports.

## Future Roadmap

- Add portfolio analytics and risk metrics.
- Expand options analytics with Greeks and volatility modeling.
- Add backtesting support for quantitative strategies.
- Integrate broker and market-data provider adapters.
- Build automated report generation workflows.
- Add dashboards and richer notebook examples.

## License

This project is licensed under the MIT License. See `LICENSE` for details.
