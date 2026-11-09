"""
DRISHTI — Stock & Price Analysis Service
Executes parameterized queries against COMPANIES and DAILY_PRICES in IBM Db2.
"""
from typing import List, Dict, Any, Optional
from datetime import date
from backend.core.db2 import fetch_all, fetch_one, execute_statement

def get_all_companies() -> List[Dict[str, Any]]:
    """Retrieve all tracked companies with latest close price and volume."""
    sql = """
        SELECT 
            c.stock_id,
            c.ticker,
            c.company_name,
            c.sector,
            c.industry,
            c.market_cap,
            c.currency,
            p.close_price AS latest_close,
            p.daily_return_pct AS daily_change_pct,
            p.volume AS latest_volume,
            p.trading_date AS latest_date
        FROM COMPANIES c
        LEFT JOIN (
            SELECT p1.stock_id, p1.close_price, p1.daily_return_pct, p1.volume, p1.trading_date
            FROM DAILY_PRICES p1
            INNER JOIN (
                SELECT stock_id, MAX(trading_date) AS max_date
                FROM DAILY_PRICES
                GROUP BY stock_id
            ) p2 ON p1.stock_id = p2.stock_id AND p1.trading_date = p2.max_date
        ) p ON c.stock_id = p.stock_id
        ORDER BY c.ticker ASC
    """
    return fetch_all(sql)

def get_company_by_ticker(ticker: str) -> Optional[Dict[str, Any]]:
    """Get company details by ticker symbol."""
    sql = """
        SELECT stock_id, ticker, company_name, sector, industry, market_cap, currency, created_at
        FROM COMPANIES
        WHERE UPPER(ticker) = UPPER(?)
    """
    return fetch_one(sql, (ticker.strip(),))

def get_stock_price_history(
    stock_id: int,
    limit: int = 180,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
) -> List[Dict[str, Any]]:
    """Retrieve historical daily prices for a given stock ordered chronologically."""
    params = [stock_id]
    date_filter = ""
    
    if start_date:
        date_filter += " AND trading_date >= ?"
        params.append(start_date)
    if end_date:
        date_filter += " AND trading_date <= ?"
        params.append(end_date)
        
    sql = f"""
        SELECT price_id, stock_id, trading_date, open_price, high_price,
               low_price, close_price, volume, vwap, daily_return_pct
        FROM DAILY_PRICES
        WHERE stock_id = ? {date_filter}
        ORDER BY trading_date DESC
        FETCH FIRST {int(limit)} ROWS ONLY
    """
    rows = fetch_all(sql, tuple(params))
    # Return in ascending order for standard charting
    rows.reverse()
    return rows

def get_stock_metrics_summary(stock_id: int) -> Dict[str, Any]:
    """Calculate key 30-day and 52-week summary metrics."""
    sql = """
        SELECT 
            COUNT(*) AS total_records,
            MAX(high_price) AS fifty_two_week_high,
            MIN(low_price) AS fifty_two_week_low,
            AVG(CAST(volume AS DOUBLE)) AS avg_volume
        FROM DAILY_PRICES
        WHERE stock_id = ?
    """
    metrics = fetch_one(sql, (stock_id,)) or {}
    
    # 30-day return calculation
    thirty_day_sql = """
        SELECT close_price, trading_date
        FROM DAILY_PRICES
        WHERE stock_id = ?
        ORDER BY trading_date DESC
        FETCH FIRST 30 ROWS ONLY
    """
    recent_prices = fetch_all(thirty_day_sql, (stock_id,))
    thirty_day_return = 0.0
    if len(recent_prices) >= 2:
        latest = float(recent_prices[0]["close_price"])
        oldest = float(recent_prices[-1]["close_price"])
        if oldest > 0:
            thirty_day_return = round(((latest - oldest) / oldest) * 100, 2)
            
    return {
        "total_records": metrics.get("total_records", 0),
        "fifty_two_week_high": metrics.get("fifty_two_week_high"),
        "fifty_two_week_low": metrics.get("fifty_two_week_low"),
        "average_volume_30d": metrics.get("avg_volume"),
        "thirty_day_return_pct": thirty_day_return
    }

