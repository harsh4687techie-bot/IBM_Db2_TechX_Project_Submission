"""
DRISHTI — Sector Performance Models
"""
from typing import Optional, List
from datetime import date, datetime
from pydantic import BaseModel

class SectorMetricItem(BaseModel):
    metric_id: int
    sector: str
    metric_date: date
    avg_return_pct: Optional[float] = None
    total_volume: Optional[int] = None
    top_performer_ticker: Optional[str] = None
    lagging_ticker: Optional[str] = None
    volatility_index: Optional[float] = None
    calculated_at: Optional[datetime] = None

class SectorOverviewItem(BaseModel):
    sector: str
    stock_count: int
    avg_market_cap: Optional[float] = None
    latest_avg_return_pct: Optional[float] = None
    total_sector_volume: Optional[int] = None
    top_stock: Optional[str] = None
    anomaly_count: int = 0

