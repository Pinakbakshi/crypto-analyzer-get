"""API-level tests for the technical-signal route; no live exchange calls."""
import unittest
from unittest.mock import AsyncMock, patch

import pandas as pd
from fastapi.testclient import TestClient

from app.core.settings import settings
from app.main import app


def candles_frame(count: int = 100) -> pd.DataFrame:
    close = [100.0 + i * 0.8 for i in range(count)]
    return pd.DataFrame({
        "ts": pd.date_range("2026-01-01", periods=count, freq="h", tz="UTC"),
        "open": close,
        "high": [v + 1 for v in close],
        "low": [v - 1 for v in close],
        "close": close,
        "vol_base": [1000.0 + i for i in range(count)],
    })


class TechnicalSignalRouteTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.headers = {"X-API-Key": settings.API_KEY}

    def test_route_rejects_missing_api_key(self):
        response = self.client.get(
            "/analysis/technical-signal",
            params={"symbol": "BTCUSDT"},
        )
        self.assertEqual(response.status_code, 401)

    def test_route_returns_verifiable_analysis_without_live_exchange(self):
        with patch(
            "app.routes.analysis.bitget.candles",
            new=AsyncMock(return_value=candles_frame()),
        ) as candles_mock:
            response = self.client.get(
                "/analysis/technical-signal",
                params={"symbol": "btcusdt", "timeframe": "1h", "limit": 100},
                headers=self.headers,
            )

        self.assertEqual(response.status_code, 200, response.text)
        payload = response.json()
        self.assertEqual(payload["symbol"], "BTCUSDT")
        self.assertEqual(payload["timeframe"], "1h")
        analysis = payload["analysis"]
        self.assertIn(analysis["signal"], {"bullish_bias", "bearish_bias", "neutral_or_mixed"})
        self.assertGreaterEqual(analysis["score"], -100)
        self.assertLessEqual(analysis["score"], 100)
        self.assertTrue(analysis["components"])
        self.assertTrue(analysis["drivers"])
        self.assertIn("scenario_levels", analysis)
        self.assertIn("not a probability", analysis["signal_strength_note"])
        candles_mock.assert_awaited_once_with("BTCUSDT", "1h", 100, None)


if __name__ == "__main__":
    unittest.main()
