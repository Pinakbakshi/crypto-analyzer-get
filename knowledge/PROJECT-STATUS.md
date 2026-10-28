# Project status

Review date: 2026-10-29  
Branch: feat/forgepilot-signal-analysis  
State: Implementation committed to a review branch; verification pending.

## Product goal
Provide a crypto market-analysis API that fetches exchange candles and explains technical context and directional bias without implying certainty.

## This change
- Adds an explainable rule-based technical-signal endpoint.
- Includes score components, indicator values, recent range levels, reasons, and limitations.
- Does not submit orders, use exchange trading credentials, or claim calibrated forecast probabilities.

## Known gaps
- Test suite has not been run in this environment.
- GitHub Actions result has not been inspected.
- No live API contract test for Bitget v2 endpoints.
- No historical walk-forward backtest or benchmark against buy-and-hold / simple baselines.
- No calibrated ML forecast, uncertainty interval, or probability of profit.
- Existing provider API version needs a separate compatibility review against current Bitget docs.
- Existing application has other security and reliability concerns that were not changed in this slice; review authentication coverage, external error leakage, alert side effects, CORS, timeouts, and rate limiting before public production use.

## Release gate
Do not merge or deploy as a validated prediction until unit/endpoint tests pass, the Bitget contract is verified, and any strategy claims are supported by leakage-safe out-of-sample results including realistic trading costs.
