"""
DRISHTI — Stocks & Prices API Router
"""
from typing import List, Optional
from datetime import date
from fastapi import APIRouter, HTTPException, Query
from backend.services.stock_service import (
    get_all_companies,
    get_company_by_ticker,
    get_stock_price_history,
    get_stock_metrics_summary
)
from backend.models.stock import StockDetailResponse, CompanyResponse

router = APIRouter(prefix="/api/stocks", tags=["Stocks"])

@router.get("")
def list_stocks():
    """Retrieve all tracked companies with latest price and volume."""
    return get_all_companies()

@router.get("/{ticker}")
def get_stock_detail(ticker: str):
    """Retrieve stock profile, latest price, and 30d/52w performance metrics."""
    comp = get_company_by_ticker(ticker)
    if not comp:
        raise HTTPException(status_code=404, detail=f"Stock ticker '{ticker}' not found.")
        
    metrics = get_stock_metrics_summary(comp["stock_id"])
    prices = get_stock_price_history(comp["stock_id"], limit=1)
    latest_price = prices[0] if prices else None
    
    return {
        "company": comp,
        "latest_price": latest_price,
        "metrics": metrics
    }

@router.get("/{ticker}/prices")
def get_stock_prices(
    ticker: str,
    limit: int = Query(90, ge=1, le=365),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
):
    """Retrieve chronological daily price series for charting."""
    comp = get_company_by_ticker(ticker)
    if not comp:
        raise HTTPException(status_code=404, detail=f"Stock ticker '{ticker}' not found.")
        
    return get_stock_price_history(
        stock_id=comp["stock_id"],
        limit=limit,
        start_date=start_date,
        end_date=end_date
    )

