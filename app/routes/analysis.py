"""Explainable technical-signal analysis endpoint."""
from fastapi import APIRouter, HTTPException, Query

from ..core.settings import settings
from ..core.signal_engine import analyze_candles
from ..services import bitget

router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.get(
    "/technical-signal",
    summary="Explainable technical market-bias analysis",
    description=(
        "Returns a deterministic, weighted technical-indicator confluence score. "
        "It is a directional-bias heuristic, not a trained prediction model or "
        "a probability of profit."
    ),
)
async def technical_signal(
    symbol: str = Query(..., min_length=3, max_length=30, description="Trading symbol, e.g. BTCUSDT"),
    granularity: str = Query("1h", description="Candle timeframe supported by Bitget"),
    timeframe: str | None = Query(None, description="Alias for granularity"),
    limit: int = Query(200, ge=30, le=settings.MAX_CANDLES),
    product_type: str | None = Query(None, description="Optional futures product type"),
):
    resolved_timeframe = timeframe or granularity
    normalized_symbol = symbol.strip().upper()
    if not normalized_symbol:
        raise HTTPException(status_code=422, detail="symbol must not be blank")
    frame = await bitget.candles(normalized_symbol, resolved_timeframe, limit, product_type)
    return {
        "symbol": normalized_symbol,
        "timeframe": resolved_timeframe,
        "source": "Bitget market candles",
        "analysis": analyze_candles(frame),
    }
