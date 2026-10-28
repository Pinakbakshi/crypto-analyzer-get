# Trend-to-implementation log

## 2026-10-29 — Evidence-first signal analysis

### Finding: Karpathy autoresearch uses fixed-budget experiments and a validation metric
- Source URL: https://github.com/karpathy/autoresearch
- Source type: Official repository
- Retrieved at: 2026-10-29
- Version/commit: Default branch reviewed; commit SHA not pinned in this log.
- What changed: The reviewed README describes a small LLM training setup where an agent changes a bounded set of training code, runs experiments for a fixed wall-clock budget, and keeps/discards changes based on validation bits-per-byte.
- Why it matters: The experiment discipline can guide future crypto-strategy comparisons, but the LLM training setup is not a market prediction method.
- Confidence: High for the README description; no evidence from this source that it improves crypto returns.
- Novelty: Known technique / applicable methodology, not a new trading algorithm.
- Project fit: Medium for research workflow; low for direct algorithm reuse.
- Risk and compatibility: Do not translate an LLM-training experiment into financial forecasting without market-specific data and out-of-sample evaluation.
- Test to validate: Candidate strategies need chronological walk-forward splits, fees, slippage, funding where applicable, and a fixed baseline.
- Decision: Adopt measurement discipline; reject direct reuse as a crypto predictor.
- Implementation status: Documentation decision recorded; no autonomous experiment runner added.

### Finding: Bitget's reviewed market-candles documentation exposes a v3 endpoint
- Source URL: https://www.bitget.com/docs/catalog/market/market-data
- Source type: Official API documentation
- Retrieved at: 2026-10-29
- What changed: The official page reviewed documents /api/v3/market/candles, with category, symbol, interval, and a maximum limit of 1,000.
- Why it matters: This repository's provider service currently requests /api/v2/spot/market/candles or /api/v2/mix/market/candles with v2-style parameter names.
- Confidence: High that the reviewed page documents the v3 contract; insufficient evidence here to conclude the current v2 paths are disabled.
- Novelty: Meaningful API-version difference identified, not yet verified as a breaking change.
- Project fit: High for a separate provider contract review.
- Risk and compatibility: Do not migrate paths and response parsing without spot/futures contract tests.
- Test to validate: Add mocked response fixtures and a safe live smoke test before migrating.
- Decision: Defer provider migration; retain current data adapter for this feature.
- Implementation status: Follow-up documented; no provider contract changed.

## Research boundary

No new, validated market-prediction algorithm was established by the primary sources reviewed for this change. The implementation is intentionally labelled a deterministic technical heuristic, not a machine-learning forecast.
