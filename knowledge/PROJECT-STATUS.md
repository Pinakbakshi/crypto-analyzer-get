# Project status

Review date: 2026-10-29  
Branch: feat/forgepilot-signal-analysis  
State: Implemented on a review branch; offline unit CI passed for the current code change.

## Product goal
Provide a crypto market-analysis API that fetches exchange candles and explains technical context and directional bias without implying certainty.

## This change
- Adds an explainable rule-based technical-signal endpoint.
- Includes score components, indicator values, recent range levels, reasons, and limitations.
- Does not submit orders, use exchange trading credentials, or claim calibrated forecast probabilities.
- GitHub Actions installed requirements successfully and passed all five offline signal-engine tests on commit c5927e2b8ec818ae3fd7bb1a6dd8b430289681cb.

## Known gaps
- No live API contract test for Bitget v2 endpoints.
- No API-level test for authentication and mocked exchange response handling.
- No historical walk-forward backtest or benchmark against buy-and-hold / simple baselines.
- No calibrated ML forecast, uncertainty interval, or probability of profit.
- Existing provider API version needs a separate compatibility review against current Bitget docs.
- Existing application has other security and reliability concerns that were not changed in this slice; review authentication coverage, external error leakage, alert side effects, CORS, timeouts, and rate limiting before public production use.
- The baseline suite was not run before edits because the local execution environment could not clone from GitHub; the new CI tests are passing, but this is not a baseline comparison.

## Release gate
Do not merge or deploy as a validated prediction until endpoint tests pass, the provider contract is verified, and any strategy claims are supported by leakage-safe out-of-sample results including realistic trading costs.
