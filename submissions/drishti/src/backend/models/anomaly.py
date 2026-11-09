"""
DRISHTI — Anomaly Data Models
"""
from typing import Optional, List
from datetime import date, datetime
from pydantic import BaseModel, Field

class AnomalyItem(BaseModel):
    anomaly_id: int
    stock_id: int
    ticker: Optional[str] = None
    company_name: Optional[str] = None
    trading_date: date
    anomaly_type: str = Field(..., description="VOLUME_SURGE, PRICE_SPIKE, VOLATILITY_BURST")
    severity: str = Field(..., description="LOW, MEDIUM, HIGH, CRITICAL")
    metric_value: Optional[float] = None
    baseline_mean: Optional[float] = None
    z_score: Optional[float] = None
    description: str
    detected_by: str = "AnomalyDetectionAgent"
    detected_at: Optional[datetime] = None

class AnomalySummary(BaseModel):
    total_anomalies: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    by_type: dict[str, int]

