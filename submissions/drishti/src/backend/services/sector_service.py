"""
DRISHTI — Sector Intelligence & Comparison Service
Aggregates cross-sectional performance, sector rotation, and risk metrics in Db2.
"""
from typing import List, Dict, Any, Optional
from datetime import date
from backend.core.db2 import fetch_all, fetch_one, execute_statement

def get_sector_overview() -> List[Dict[str, Any]]:
    """Get aggregated overview for all market sectors."""
    sql = """
        SELECT 
            c.sector,
            COUNT(DISTINCT c.stock_id) AS stock_count,
            AVG(c.market_cap) AS avg_market_cap,
            AVG(p.daily_return_pct) AS latest_avg_return_pct,
            SUM(p.volume) AS total_sector_volume
        FROM COMPANIES c
        LEFT JOIN (
            SELECT p1.stock_id, p1.daily_return_pct, p1.volume
            FROM DAILY_PRICES p1
            INNER JOIN (
                SELECT stock_id, MAX(trading_date) AS max_date
                FROM DAILY_PRICES
                GROUP BY stock_id
            ) p2 ON p1.stock_id = p2.stock_id AND p1.trading_date = p2.max_date
        ) p ON c.stock_id = p.stock_id
        GROUP BY c.sector
        ORDER BY latest_avg_return_pct DESC
    """
    sectors = fetch_all(sql)
    
    # Enrich with anomaly count per sector
    anomaly_counts_sql = """
        SELECT c.sector, COUNT(*) AS anomaly_count
        FROM MARKET_ANOMALIES a
        INNER JOIN COMPANIES c ON a.stock_id = c.stock_id
        GROUP BY c.sector
    """
    anom_rows = fetch_all(anomaly_counts_sql)
    anom_map = {r["sector"]: int(r["anomaly_count"]) for r in anom_rows}
    
    for s in sectors:
        s["anomaly_count"] = anom_map.get(s["sector"], 0)
        s["stock_count"] = int(s.get("stock_count") or 0)
        s["total_sector_volume"] = int(s.get("total_sector_volume") or 0)
        if s.get("latest_avg_return_pct") is not None:
            s["latest_avg_return_pct"] = round(float(s["latest_avg_return_pct"]), 2)
        else:
            s["latest_avg_return_pct"] = 0.0
            
        if s.get("avg_market_cap") is not None:
            s["avg_market_cap"] = round(float(s["avg_market_cap"]), 2)
        else:
            s["avg_market_cap"] = 0.0
            
    return sectors

def get_sector_stocks(sector_name: str) -> List[Dict[str, Any]]:
    """Retrieve all stocks belonging to a specific sector."""
    sql = """
        SELECT 
            c.stock_id,
            c.ticker,
            c.company_name,
            c.industry,
            c.market_cap,
            p.close_price AS latest_close,
            p.daily_return_pct AS latest_return_pct,
            p.volume AS latest_volume
        FROM COMPANIES c
        LEFT JOIN (
            SELECT p1.stock_id, p1.close_price, p1.daily_return_pct, p1.volume
            FROM DAILY_PRICES p1
            INNER JOIN (
                SELECT stock_id, MAX(trading_date) AS max_date
                FROM DAILY_PRICES
                GROUP BY stock_id
            ) p2 ON p1.stock_id = p2.stock_id AND p1.trading_date = p2.max_date
        ) p ON c.stock_id = p.stock_id
        WHERE UPPER(c.sector) = UPPER(?)
        ORDER BY p.daily_return_pct DESC
    """
    return fetch_all(sql, (sector_name.strip(),))

def recalculate_sector_metrics() -> int:
    """
    Calculates daily sector rollups and inserts them into SECTOR_METRICS
    with duplicate prevention.
    """
    # Find distinct dates and sectors
    sql = """
        SELECT DISTINCT c.sector, p.trading_date
        FROM DAILY_PRICES p
        INNER JOIN COMPANIES c ON p.stock_id = c.stock_id
        ORDER BY p.trading_date DESC
        FETCH FIRST 60 ROWS ONLY
    """
    pairs = fetch_all(sql)
    inserted = 0
    
    for pair in pairs:
        sec = pair["sector"]
        t_date = pair["trading_date"]
        
        # Check if already calculated
        chk_sql = "SELECT COUNT(*) AS cnt FROM SECTOR_METRICS WHERE sector = ? AND metric_date = ?"
        chk = fetch_one(chk_sql, (sec, t_date))
        if chk and int(chk.get("cnt", 0)) > 0:
            continue
            
        calc_sql = """
            SELECT 
                AVG(p.daily_return_pct) AS avg_return,
                SUM(p.volume) AS total_vol
            FROM DAILY_PRICES p
            INNER JOIN COMPANIES c ON p.stock_id = c.stock_id
            WHERE c.sector = ? AND p.trading_date = ?
        """
        agg = fetch_one(calc_sql, (sec, t_date))
        if agg:
            avg_ret = agg.get("avg_return")
            total_vol = agg.get("total_vol")
            insert_sql = """
                INSERT INTO SECTOR_METRICS (
                    sector, metric_date, avg_return_pct, total_volume
                ) VALUES (?, ?, ?, ?)
            """
            execute_statement(insert_sql, (sec, t_date, avg_ret, total_vol))
            inserted += 1
            
    return inserted

