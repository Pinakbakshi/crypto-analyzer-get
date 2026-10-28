"""Offline tests for the explainable technical-signal engine."""
import unittest

import pandas as pd

from app.core.signal_engine import analyze_candles


def make_frame(direction: str, count: int = 100) -> pd.DataFrame:
    if direction == "up":
        close = [100.0 + i * 1.5 for i in range(count)]
    elif direction == "down":
        close = [250.0 - i * 1.5 for i in range(count)]
    else:
        close = [100.0 + (1.0 if i % 2 else -1.0) for i in range(count)]
    return pd.DataFrame({
        "ts": pd.date_range("2026-01-01", periods=count, freq="h", tz="UTC"),
        "open": close,
        "high": [value + 1 for value in close],
        "low": [value - 1 for value in close],
        "close": close,
        "vol_base": [1000 + (i % 7) * 10 for i in range(count)],
    })


class SignalEngineTests(unittest.TestCase):
    def test_uptrend_produces_bullish_bias(self):
        result = analyze_candles(make_frame("up"))
        self.assertEqual(result["signal"], "bullish_bias")
        self.assertGreater(result["score"], 0)
        self.assertLessEqual(result["score"], 100)

    def test_downtrend_produces_bearish_bias(self):
        result = analyze_candles(make_frame("down"))
        self.assertEqual(result["signal"], "bearish_bias")
        self.assertLess(result["score"], 0)
        self.assertGreaterEqual(result["score"], -100)

    def test_result_explains_score_and_disclaims_probability(self):
        result = analyze_candles(make_frame("up"))
        self.assertTrue(result["components"])
        self.assertTrue(result["drivers"])
        self.assertIn("not a probability", result["signal_strength_note"])
        self.assertIn("scenario_levels", result)

    def test_rejects_insufficient_candles(self):
        with self.assertRaisesRegex(ValueError, "At least 30 candles"):
            analyze_candles(make_frame("up", 29))

    def test_rejects_missing_ohlc_columns(self):
        with self.assertRaisesRegex(ValueError, "Missing required candle columns"):
            analyze_candles(pd.DataFrame({"close": range(30)}))


if __name__ == "__main__":
    unittest.main()
