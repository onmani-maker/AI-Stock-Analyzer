# AI Stock Analyzer

AI Stock Analyzer is an open-source Python project for analyzing U.S. stocks and options with the help of technical indicators, market screening workflows, and AI-powered reporting.

The project is designed as a clean foundation for research, analytics, and future quantitative trading features.

## Features

- Analyze U.S. equity price history and summary statistics.
- Analyze options chains, including moneyness, basic contract metrics, and Black-Scholes Greeks.
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

Download and display an options chain with `yfinance`. Run the command without `--expiration` first to list the dates currently available from `yfinance`; when no expiration is provided, the app downloads the earliest available chain. To download a different chain, choose one of the listed dates and pass it with `--expiration`. The command saves CSV files under `data/options/` and displays Strike, Bid, Ask, Last Price, Volume, Open Interest, and Implied Volatility:

```bash
python src/main.py --ticker AAPL --options
```

```bash
python src/main.py --ticker AAPL --options --expiration <YYYY-MM-DD>
```

Use the reusable options helpers directly from Python:

```python
from option_analysis import download_option_chain, list_option_expirations

expirations = list_option_expirations("AAPL")
print(expirations)

chain = download_option_chain("AAPL", expiration=expirations[0])
print(f"Calls saved to {chain.calls_path}")
print(f"Puts saved to {chain.puts_path}")
print(chain.calls.head())
print(chain.puts.head())
```


Calculate Black-Scholes option Greeks (Delta, Gamma, Theta, Vega, and Rho) for a single call or put option. Inputs are current stock price, strike price, time to expiration in years, annualized risk-free rate as a decimal, annualized implied volatility as a decimal, and option type:

```bash
python src/main.py --greeks \
  --stock-price 190 \
  --strike-price 195 \
  --time-to-expiration 0.5 \
  --risk-free-rate 0.05 \
  --implied-volatility 0.25 \
  --option-type call
```

Calculate put Greeks from Python and receive the results as a pandas DataFrame:

```python
from option_analysis import calculate_option_greeks

greeks = calculate_option_greeks(
    stock_price=190,
    strike_price=195,
    time_to_expiration=0.5,
    risk_free_rate=0.05,
    implied_volatility=0.25,
    option_type="put",
)
print(greeks)
```

The returned DataFrame includes the normalized input assumptions plus `Delta`, `Gamma`, `Theta`, `Vega`, and `Rho`. Theta is annualized; Vega and Rho are sensitivities to a 1.00 absolute change in implied volatility and risk-free rate respectively.

Display the latest SMA, EMA, RSI, MACD, and Bollinger Band values for a ticker:

```python
from stock_analysis import analyze_stock, format_indicator_table

summary, enriched_history = analyze_stock("AAPL", period="1y", interval="1d")

print(f"Ticker: {summary.ticker}")
print(format_indicator_table(enriched_history))
```

Example output:

```text
               Indicator  Value
                SMA (20) 192.14
                SMA (50) 187.63
                EMA (20) 193.02
                RSI (14)  58.41
                    MACD   2.18
             MACD Signal   1.76
          MACD Histogram   0.42
 Bollinger Upper (20, 2) 202.59
   Bollinger Middle (20) 192.14
 Bollinger Lower (20, 2) 181.69
```

## Future Roadmap

- Add portfolio analytics and risk metrics.
- Expand options analytics with volatility modeling and strategy payoff analysis.
- Add backtesting support for quantitative strategies.
- Integrate broker and market-data provider adapters.
- Build automated report generation workflows.
- Add dashboards and richer notebook examples.

## License

This project is licensed under the MIT License. See `LICENSE` for details.
