"""
DRISHTI — Stock & Price Pydantic Models
"""
from typing import Optional, List
from datetime import date, datetime
from pydantic import BaseModel, Field

class CompanyBase(BaseModel):
    ticker: str = Field(..., max_length=16, description="Stock ticker symbol, e.g. AAPL")
    company_name: str = Field(..., max_length=128, description="Full company name")
    sector: str = Field(..., max_length=64, description="Economic sector")
    industry: Optional[str] = Field(None, max_length=128, description="Specific industry")
    market_cap: Optional[float] = Field(None, description="Market capitalization in USD")
    currency: str = Field("USD", max_length=8)

class CompanyCreate(CompanyBase):
    pass

class CompanyResponse(CompanyBase):
    stock_id: int
    created_at: Optional[datetime] = None

class DailyPriceBase(BaseModel):
    trading_date: date
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    volume: int
    vwap: Optional[float] = None
    daily_return_pct: Optional[float] = None

class DailyPriceResponse(DailyPriceBase):
    price_id: int
    stock_id: int

class StockDetailResponse(BaseModel):
    company: CompanyResponse
    latest_price: Optional[DailyPriceResponse] = None
    total_records: int
    thirty_day_return_pct: Optional[float] = None
    average_volume_30d: Optional[float] = None
    fifty_two_week_high: Optional[float] = None
    fifty_two_week_low: Optional[float] = None

class StockSummaryItem(BaseModel):
    stock_id: int
    ticker: str
    company_name: str
    sector: str
    latest_close: Optional[float] = None
    daily_change_pct: Optional[float] = None
    latest_volume: Optional[int] = None
    latest_date: Optional[date] = None

