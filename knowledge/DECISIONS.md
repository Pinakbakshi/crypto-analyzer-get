# Engineering decisions

## D-001 — Add explainable technical-signal analysis before a trained predictor
Status: Accepted, 2026-10-29.

Decision: Add GET /analysis/technical-signal with a deterministic weighted confluence score based on moving-average trend, RSI momentum, MACD-vs-signal, and close-vs-SMA20.

Why: The repository already fetches candles and has a technical-indicator dependency, but the exposed candle endpoint does not provide an integrated, documented decision rationale. A small rule-based vertical slice is testable and inspectable without training data or claims about forecast accuracy.

Not a prediction model: the score is bounded to [-100, 100], but it is not a probability, expected return, entry signal guarantee, or profit estimate. It does not place orders.

Alternatives considered:
- Add a new LSTM/Transformer immediately: deferred because there is no checked-in historical dataset, leakage-safe training/evaluation pipeline, baseline metrics, or evidence that a deep model beats a simple baseline.
- Migrate Bitget v2 API calls to v3 in the same patch: deferred because the response schema and spot/futures mapping need contract tests.
- Add more indicators: rejected for now; indicator count is not evidence of predictive value.

## D-002 — Keep API integration thin and computation pure
Status: Accepted, 2026-10-29.
- app/routes/analysis.py fetches market candles and returns analysis.
- app/core/signal_engine.py computes deterministic analysis without network calls.
- Tests use synthetic candles and do not depend on external market APIs or credentials.

## D-003 — Treat signal strength as heuristic magnitude
Status: Accepted, 2026-10-29.

Signal labels describe rule-score magnitude only. They must never be presented as calibrated confidence or likelihood of a profitable trade.
