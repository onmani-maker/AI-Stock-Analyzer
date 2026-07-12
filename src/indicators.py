"""Reusable technical indicator calculations for market analysis."""

from __future__ import annotations

import pandas as pd


def _require_series(values: pd.Series, name: str = "values") -> pd.Series:
    """Return a numeric series after validating indicator input."""
    if values.empty:
        raise ValueError(f"{name} must contain at least one row.")
    return pd.to_numeric(values, errors="coerce")


def calculate_sma(close: pd.Series, window: int) -> pd.Series:
    """Calculate a simple moving average over ``window`` periods."""
    close = _require_series(close, "close")
    return close.rolling(window=window, min_periods=window).mean()


def calculate_ema(close: pd.Series, span: int) -> pd.Series:
    """Calculate an exponential moving average over ``span`` periods."""
    close = _require_series(close, "close")
    return close.ewm(span=span, adjust=False, min_periods=span).mean()


def calculate_rsi(close: pd.Series, window: int = 14) -> pd.Series:
    """Calculate the Relative Strength Index (RSI) over ``window`` periods."""
    close = _require_series(close, "close")
    delta = close.diff()
    gains = delta.clip(lower=0)
    losses = -delta.clip(upper=0)

    average_gain = gains.ewm(alpha=1 / window, adjust=False, min_periods=window).mean()
    average_loss = losses.ewm(alpha=1 / window, adjust=False, min_periods=window).mean()
    relative_strength = average_gain / average_loss
    rsi = 100 - (100 / (1 + relative_strength))

    return rsi.where(average_loss != 0, 100.0).where(average_gain != 0, 0.0)


def calculate_macd(
    close: pd.Series,
    fast_span: int = 12,
    slow_span: int = 26,
    signal_span: int = 9,
) -> pd.DataFrame:
    """Calculate MACD, signal line, and histogram values."""
    close = _require_series(close, "close")
    fast_ema = close.ewm(span=fast_span, adjust=False, min_periods=fast_span).mean()
    slow_ema = close.ewm(span=slow_span, adjust=False, min_periods=slow_span).mean()
    macd = fast_ema - slow_ema
    signal = macd.ewm(span=signal_span, adjust=False, min_periods=signal_span).mean()

    return pd.DataFrame(
        {
            "macd": macd,
            "macd_signal": signal,
            "macd_histogram": macd - signal,
        },
        index=close.index,
    )


def calculate_bollinger_bands(
    close: pd.Series,
    window: int = 20,
    num_std: float = 2,
) -> pd.DataFrame:
    """Calculate Bollinger Bands using a moving average and standard deviation."""
    close = _require_series(close, "close")
    middle = calculate_sma(close, window)
    rolling_std = close.rolling(window=window, min_periods=window).std()
    upper = middle + (rolling_std * num_std)
    lower = middle - (rolling_std * num_std)

    return pd.DataFrame(
        {
            "bb_upper": upper,
            "bb_middle": middle,
            "bb_lower": lower,
        },
        index=close.index,
    )


def add_technical_indicators(history: pd.DataFrame) -> pd.DataFrame:
    """Return price history with standard technical indicators appended."""
    if history.empty:
        raise ValueError("History must contain at least one row.")
    if "Close" not in history.columns:
        raise ValueError("History must include a Close column.")

    enriched = history.copy()
    close = pd.to_numeric(enriched["Close"], errors="coerce")

    enriched["sma_20"] = calculate_sma(close, 20)
    enriched["sma_50"] = calculate_sma(close, 50)
    enriched["ema_20"] = calculate_ema(close, 20)
    enriched["rsi_14"] = calculate_rsi(close, 14)
    enriched = enriched.join(calculate_macd(close))
    enriched = enriched.join(calculate_bollinger_bands(close, 20, 2))

    return enriched
