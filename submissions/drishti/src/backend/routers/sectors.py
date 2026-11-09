"""
DRISHTI — Sector Intelligence API Router
"""
from fastapi import APIRouter
from backend.services.sector_service import (
    get_sector_overview,
    get_sector_stocks,
    recalculate_sector_metrics
)

router = APIRouter(prefix="/api/sectors", tags=["Sectors"])

@router.get("")
def list_sectors():
    """Retrieve sector-level performance rollups, volumes, and anomaly counts."""
    return get_sector_overview()

@router.get("/{sector}/stocks")
def get_stocks_in_sector(sector: str):
    """Retrieve all company holdings and performance within a sector."""
    return get_sector_stocks(sector)

@router.post("/recalculate")
def trigger_recalculation():
    """Recalculates daily sector metrics in Db2."""
    inserted = recalculate_sector_metrics()
    return {
        "status": "success",
        "sector_metric_records_created": inserted
    }

