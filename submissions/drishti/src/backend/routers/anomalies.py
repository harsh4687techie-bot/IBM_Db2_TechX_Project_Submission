"""
DRISHTI — Market Anomalies API Router
"""
from typing import Optional
from fastapi import APIRouter, Query
from backend.services.anomaly_service import (
    get_anomalies,
    get_anomaly_summary,
    run_anomaly_detection_scan
)

router = APIRouter(prefix="/api/anomalies", tags=["Anomalies"])

@router.get("")
def list_anomalies(
    stock_id: Optional[int] = None,
    severity: Optional[str] = None,
    anomaly_type: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200)
):
    """Retrieve detected volume surges, price spikes, and volatility bursts."""
    return get_anomalies(
        stock_id=stock_id,
        severity=severity,
        anomaly_type=anomaly_type,
        limit=limit
    )

@router.get("/summary")
def get_summary():
    """Retrieve aggregate anomaly statistics and severity distribution."""
    return get_anomaly_summary()

@router.post("/scan")
def trigger_scan(stock_id: Optional[int] = None):
    """Triggers the statistical anomaly detection scan across price series."""
    count = run_anomaly_detection_scan(stock_id=stock_id)
    return {
        "status": "success",
        "new_anomalies_identified": count
    }

