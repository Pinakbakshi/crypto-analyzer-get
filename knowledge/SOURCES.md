# Verified primary sources

Retrieved for the ForgePilot implementation review on 2026-10-29. “Current” means observed during this review, not a guarantee that a page will never change.

| Source | What it supports | Application decision |
|---|---|---|
| Andrej Karpathy, autoresearch repository: https://github.com/karpathy/autoresearch | Fixed-budget experiments, explicit evaluation metric, and keeping/discarding changes based on measured results. The README describes a GPU-bound LLM-training experiment, not a cryptocurrency prediction algorithm. | Adopt the evaluation discipline for future strategy research; do not copy its training architecture into this API. |
| Bitget market-data documentation: https://www.bitget.com/docs/catalog/market/market-data | Current public candle API documentation, including supported intervals, response shape, and limits. The reviewed page documents /api/v3/market/candles; this repository currently uses v2 spot/mix candle paths. | Keep existing provider behavior in this change; separately contract-test and plan any v2-to-v3 migration. |
| FastAPI testing guide: https://fastapi.tiangolo.com/tutorial/testing/ | Supports pytest/TestClient-based endpoint tests. | Add deterministic offline unit tests now; add API integration tests with mocked Bitget responses next. |
| FastAPI async testing guide: https://fastapi.tiangolo.com/advanced/async-tests/ | Documents async testing using HTTPX and ASGI transport. | Use when endpoint-level tests are introduced. |
| pandas-ta-openbb indicator documentation: https://docs.openbb.co/odp/python/extensions/infrastructure/openbb-charting/indicators | Documents common technical indicators and their required inputs. | Keep the first signal engine small and transparent; avoid adding indicators merely to inflate a score. |

## Andrej Karpathy relevance note

The reviewed autoresearch README describes autonomous LLM-training experiments with a fixed time budget and validation bits-per-byte metric. It does not validate a “best” crypto prediction algorithm. Its transferable idea is disciplined, measurable experimentation, which this project should apply to walk-forward backtests and strategy comparison.
