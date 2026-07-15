"""Tests for option analysis helpers."""

from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC_DIR))

from option_analysis import calculate_option_greeks  # noqa: E402


class CalculateOptionGreeksValidationTest(unittest.TestCase):
    """Validate Black-Scholes Greeks input handling."""

    def test_rejects_non_finite_numeric_inputs(self) -> None:
        base_inputs = {
            "stock_price": 100.0,
            "strike_price": 100.0,
            "time_to_expiration": 1.0,
            "risk_free_rate": 0.05,
            "implied_volatility": 0.2,
            "option_type": "call",
        }
        invalid_values = (math.nan, math.inf, -math.inf)
        numeric_fields = (
            "stock_price",
            "strike_price",
            "time_to_expiration",
            "risk_free_rate",
            "implied_volatility",
        )

        for field in numeric_fields:
            for invalid_value in invalid_values:
                with self.subTest(field=field, invalid_value=invalid_value):
                    inputs = base_inputs.copy()
                    inputs[field] = invalid_value
                    with self.assertRaisesRegex(ValueError, "finite number"):
                        calculate_option_greeks(**inputs)

    def test_rejects_non_positive_inputs_that_must_be_positive(self) -> None:
        base_inputs = {
            "stock_price": 100.0,
            "strike_price": 100.0,
            "time_to_expiration": 1.0,
            "risk_free_rate": 0.05,
            "implied_volatility": 0.2,
            "option_type": "put",
        }
        positive_fields = (
            "stock_price",
            "strike_price",
            "time_to_expiration",
            "implied_volatility",
        )

        for field in positive_fields:
            with self.subTest(field=field):
                inputs = base_inputs.copy()
                inputs[field] = 0.0
                with self.assertRaisesRegex(ValueError, "greater than zero"):
                    calculate_option_greeks(**inputs)


if __name__ == "__main__":
    unittest.main()
