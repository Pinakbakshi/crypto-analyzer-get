"""Transparent, deterministic technical-signal analysis.

This module deliberately produces a rule-based market-bias score, not a price
forecast or a probability of profit. Keep formulas simple and testable until a
walk-forward backtest demonstrates that a more complex model adds value.
"""
from __future__ import annotations

import math
from typing import Any

import pandas as pd

MIN_CANDLES = 30


def _last_finite(series: pd.Series) -> float | None:
    values = pd.to_numeric(series, errors="coerce").dropna()
    if values.empty:
        return None
    value = float(values.iloc[-1])
    return value if math.isfinite(value) else None


def _rounded(value: float | None, digits: int = 4) -> float | None:
    if value is None or not math.isfinite(value):
        return None
    return round(value, digits)


def analyze_candles(frame: pd.DataFrame) -> dict[str, Any]:
    """Summarize OHLCV candles into an explainable directional-bias score."""
    if frame.empty or len(frame) < MIN_CANDLES:
        raise ValueError(f"At least {MIN_CANDLES} candles are required for analysis")
    missing = {"high", "low", "close"} - set(frame.columns)
    if missing:
        raise ValueError(f"Missing required candle columns: {', '.join(sorted(missing))}")

    data = frame.copy()
    for column in ("high", "low", "close"):
        data[column] = pd.to_numeric(data[column], errors="coerce")
    if "ts" in data.columns:
        data = data.sort_values("ts")
    data = data.dropna(subset=["high", "low", "close"])
    if len(data) < MIN_CANDLES:
        raise ValueError(f"At least {MIN_CANDLES} valid OHLC candles are required")
    if (data["close"] <= 0).any():
        raise ValueError("Candle close prices must be positive")

    close = data["close"].astype(float)
    high = data["high"].astype(float)
    low = data["low"].astype(float)
    sma20 = close.rolling(20, min_periods=20).mean()
    sma50 = close.rolling(50, min_periods=50).mean()

    delta = close.diff()
    gains = delta.clip(lower=0)
    losses = -delta.clip(upper=0)
    avg_gain = gains.ewm(alpha=1 / 14, adjust=False, min_periods=14).mean()
    avg_loss = losses.ewm(alpha=1 / 14, adjust=False, min_periods=14).mean()
    rs = avg_gain / avg_loss.replace(0, float("nan"))
    rsi = 100 - (100 / (1 + rs))
    rsi = rsi.mask((avg_loss == 0) & (avg_gain > 0), 100.0)
    rsi = rsi.mask((avg_gain == 0) & (avg_loss > 0), 0.0)

    ema12 = close.ewm(span=12, adjust=False, min_periods=12).mean()
    ema26 = close.ewm(span=26, adjust=False, min_periods=26).mean()
    macd_line = ema12 - ema26
    macd_signal = macd_line.ewm(span=9, adjust=False, min_periods=9).mean()

    previous_close = close.shift(1)
    true_range = pd.concat(
        [high - low, (high - previous_close).abs(), (low - previous_close).abs()],
        axis=1,
    ).max(axis=1)
    atr14 = true_range.rolling(14, min_periods=14).mean()

    latest_close = float(close.iloc[-1])
    latest_sma20 = _last_finite(sma20)
    latest_sma50 = _last_finite(sma50)
    latest_rsi = _last_finite(rsi)
    latest_macd = _last_finite(macd_line)
    latest_macd_signal = _last_finite(macd_signal)
    latest_atr = _last_finite(atr14)
    components: list[dict[str, Any]] = []

    def add_component(name: str, value: float | None, weight: float, rationale: str) -> None:
        if value is not None:
            components.append({"name": name, "score": value, "weight": weight, "rationale": rationale})

    if latest_sma50 is not None and latest_sma20 is not None:
        if latest_close > latest_sma50 and latest_sma20 > latest_sma50:
            value, reason = 1.0, "Price and SMA20 are above SMA50"
        elif latest_close < latest_sma50 and latest_sma20 < latest_sma50:
            value, reason = -1.0, "Price and SMA20 are below SMA50"
        elif latest_close > latest_sma20:
            value, reason = 0.5, "Price is above SMA20; longer trend is mixed"
        elif latest_close < latest_sma20:
            value, reason = -0.5, "Price is below SMA20; longer trend is mixed"
        else:
            value, reason = 0.0, "Moving-average trend is mixed"
        add_component("moving_average_trend", value, 0.35, reason)

    if latest_rsi is not None:
        if latest_rsi >= 55:
            value, reason = 1.0, "RSI indicates positive momentum (>= 55)"
        elif latest_rsi <= 45:
            value, reason = -1.0, "RSI indicates negative momentum (<= 45)"
        else:
            value, reason = 0.0, "RSI momentum is neutral (45-55)"
        add_component("rsi_momentum", value, 0.25, reason)

    if latest_macd is not None and latest_macd_signal is not None:
        value = 1.0 if latest_macd > latest_macd_signal else -1.0 if latest_macd < latest_macd_signal else 0.0
        reason = "MACD is above its signal line" if value > 0 else "MACD is below its signal line" if value < 0 else "MACD equals its signal line"
        add_component("macd_momentum", value, 0.30, reason)

    if latest_sma20 is not None:
        value = 1.0 if latest_close > latest_sma20 else -1.0 if latest_close < latest_sma20 else 0.0
        reason = "Close is above SMA20" if value > 0 else "Close is below SMA20" if value < 0 else "Close equals SMA20"
        add_component("price_vs_sma20", value, 0.10, reason)

    total_weight = sum(item["weight"] for item in components)
    score = 100.0 * sum(item["score"] * item["weight"] for item in components) / total_weight if total_weight else 0.0
    score = max(-100.0, min(100.0, score))
    signal = "bullish_bias" if score >= 25 else "bearish_bias" if score <= -25 else "neutral_or_mixed"
    magnitude = abs(score)
    strength = "strong" if magnitude >= 65 else "moderate" if magnitude >= 35 else "weak"

    prior_highs = high.iloc[-21:-1] if len(high) >= 21 else pd.Series(dtype=float)
    prior_lows = low.iloc[-21:-1] if len(low) >= 21 else pd.Series(dtype=float)
    recent_high = float(prior_highs.max()) if not prior_highs.empty else None
    recent_low = float(prior_lows.min()) if not prior_lows.empty else None
    volume_ratio = None
    if "vol_base" in data.columns:
        volume = pd.to_numeric(data["vol_base"], errors="coerce")
        average_volume = _last_finite(volume.rolling(20, min_periods=20).mean())
        latest_volume = _last_finite(volume)
        if average_volume is not None and average_volume > 0 and latest_volume is not None:
            volume_ratio = latest_volume / average_volume

    as_of = str(data["ts"].iloc[-1]) if "ts" in data.columns and not pd.isna(data["ts"].iloc[-1]) else None
    drivers = [item["rationale"] for item in components]
    if latest_rsi is not None and latest_rsi >= 70:
        drivers.append("RSI is elevated (>= 70); momentum may be extended")
    elif latest_rsi is not None and latest_rsi <= 30:
        drivers.append("RSI is low (<= 30); downside momentum may be extended")

    return {
        "method": "transparent_weighted_technical_confluence_v1",
        "as_of": as_of,
        "sample_size": int(len(data)),
        "close": _rounded(latest_close, 8),
        "score": round(score, 2),
        "signal": signal,
        "signal_strength": strength,
        "signal_strength_note": "Heuristic strength, not a probability or calibrated confidence",
        "components": components,
        "indicators": {
            "rsi14": _rounded(latest_rsi, 2),
            "sma20": _rounded(latest_sma20, 8),
            "sma50": _rounded(latest_sma50, 8),
            "macd": _rounded(latest_macd, 8),
            "macd_signal": _rounded(latest_macd_signal, 8),
            "atr14": _rounded(latest_atr, 8),
            "atr_pct_of_close": _rounded(latest_atr / latest_close * 100 if latest_atr is not None else None, 3),
            "latest_volume_vs_20_candle_average": _rounded(volume_ratio, 3),
        },
        "scenario_levels": {
            "prior_20_candle_high": _rounded(recent_high, 8),
            "prior_20_candle_low": _rounded(recent_low, 8),
            "note": "Reference levels only; not guaranteed support, resistance, entry, or target prices",
        },
        "drivers": drivers,
        "limitations": [
            "Rule-based technical confluence, not a trained machine-learning model or price forecast.",
            "Score is not a probability of a profitable trade.",
            "Does not include fees, slippage, funding, order-book depth, or portfolio risk.",
            "The latest exchange candle may still be forming.",
            "Validate any strategy with leakage-safe walk-forward backtests before use.",
        ],
    }
