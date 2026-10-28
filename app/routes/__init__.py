from fastapi import APIRouter
from .candles import router as candles
from .orderbook import router as orderbook
from .perp import router as perp
from .news import router as news
from .alerts import router as alerts
from .misc import router as misc
from .analysis import router as analysis

api_router = APIRouter()
for r in (candles, orderbook, perp, news, alerts, misc, analysis):
    api_router.include_router(r)
