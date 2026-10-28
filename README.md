# Crypto Analyzer GPT

> **Project status (2026-10-29):** The explainable technical-signal endpoint and its documentation are merged into `main`. GitHub Actions passed **7 tests** covering the signal engine and mocked API route. Live Bitget connectivity, production deployment, and predictive performance have **not** been validated.


An API for crypto-market data, technical context, and alert workflows. The current implementation fetches OHLCV candles from Bitget and exposes market endpoints through FastAPI. This branch adds a transparent, deterministic technical-signal endpoint so the reasoning behind a directional bias is inspectable.

> **Important:** the technical score is a rule-based heuristic, not a trained machine-learning forecast, a probability of profit, or financial advice. It does not execute trades.

## New: explainable technical signal

### Endpoint

GET /analysis/technical-signal

The route is protected by the same X-API-Key authentication dependency as the other API routes.

Example request:

    curl -H "X-API-Key: $API_KEY"       "http://localhost:8000/analysis/technical-signal?symbol=BTCUSDT&timeframe=1h&limit=200"

Parameters:
- symbol: exchange symbol such as BTCUSDT
- granularity: candle interval; defaults to 1h
- timeframe: optional alias for granularity
- limit: 30 to the configured MAX_CANDLES (defaults to 200)
- product_type: optional Bitget futures product type

The response includes the source/timeframe, sample size, latest close, score from -100 to +100, a directional-bias label, heuristic signal-strength label, component scores and explanations, indicator values, prior 20-candle high/low reference levels, and limitations.

### How the score is formed

The score is a weighted average of available components. Missing components are omitted and the remaining weights are renormalized.

| Component | Weight | Rule |
|---|---:|---|
| Moving-average trend | 35% | Compares price and SMA20 with SMA50; partial score when longer trend is mixed |
| RSI momentum | 25% | RSI >= 55 is positive; RSI <= 45 is negative; otherwise neutral |
| MACD momentum | 30% | MACD above/below its signal line |
| Price vs SMA20 | 10% | Close above/below SMA20 |

The weighted result is scaled to -100..+100. Scores >= 25 are labelled bullish_bias; scores <= -25 bearish_bias; values in between neutral_or_mixed. Strength labels are based only on score magnitude: weak below 35, moderate from 35, strong from 65. They are not calibrated confidence or probability.

Additional context includes RSI(14), SMA20, SMA50, MACD and signal line, ATR(14), ATR as a percentage of close, relative volume when volume is available, and the prior 20-candle high/low. Those range levels are references, not guaranteed support/resistance or trade targets.

### Why not claim an “AI prediction” yet?

The repository does not currently include a verified, leakage-safe training dataset, a walk-forward evaluation harness, or evidence that a complex model beats simple baselines after realistic fees and slippage. The first step is a transparent baseline that can be tested. A future model should only be adopted after out-of-sample results demonstrate incremental value.

## Run locally

1. Use Python 3.11.
2. Create a virtual environment and install dependencies:

       python3 -m venv .venv
       source .venv/bin/activate
       python -m pip install -r requirements.txt

3. Copy .env.example to .env and set a unique API_KEY. Configure optional provider credentials only when needed. Never commit .env or live credentials.
4. Start the API:

       uvicorn app.main:app --host 127.0.0.1 --port 8000

5. Open /docs for the generated API reference. The public /health route is informational only; protected API routes require X-API-Key.

## Tests

Run the offline signal-engine tests:

    API_KEY=ci-only-test-key-123456789 python -m unittest discover -s tests -v

The test cases use synthetic candle data and do not validate live exchange connectivity or predictive performance. GitHub Actions is configured to install requirements and run this test command on feature-branch pushes and pull requests. Check the workflow result before treating the branch as verified.

## Data and limitations

- Data source: Bitget candle endpoints used by the current adapter.
- A latest exchange candle may still be forming.
- The score does not include order-book depth, market impact, fees, slippage, derivatives funding, portfolio exposure, or event risk.
- Technical indicators can disagree and can fail in sideways or regime-changing markets.
- No live trading or order placement is implemented by this endpoint.
- The currently reviewed Bitget documentation includes a v3 candles API, while this codebase still uses v2 paths. That migration is tracked separately because the request/response contract needs tests first.

## Security

- Keep API keys, Telegram tokens, database URLs, and other credentials in environment configuration or a secret manager.
- Do not expose the development server directly to the public internet.
- Review CORS, rate limiting, error logging, alert side effects, and deployment configuration before public production use.

## Engineering notes

See knowledge/SOURCES.md for primary references, knowledge/TREND-LOG.md for evidence and applicability, knowledge/DECISIONS.md for implementation choices, and knowledge/IMPLEMENTATION-LOG.md for verification status and rollback notes.

## Disclaimer

For educational and research use only. Crypto markets are volatile; this API does not provide financial advice or guarantee future results. Backtest any strategy with chronological walk-forward splits and realistic costs before considering real-world use.
