"""
DRISHTI — Statistical Anomaly Detection Service
Identifies unusual volume surges, price spikes, and volatility bursts using
rolling statistical baselines and z-scores stored in IBM Db2.
"""
from typing import List, Dict, Any, Optional
from datetime import date
import pandas as pd
import numpy as np

from backend.core.db2 import fetch_all, fetch_one, execute_statement

def get_anomalies(
    stock_id: Optional[int] = None,
    severity: Optional[str] = None,
    anomaly_type: Optional[str] = None,
    limit: int = 100
) -> List[Dict[str, Any]]:
    """Retrieve detected anomalies joined with company ticker and name."""
    params = []
    filters = []
    
    if stock_id:
        filters.append("a.stock_id = ?")
        params.append(stock_id)
    if severity:
        filters.append("UPPER(a.severity) = UPPER(?)")
        params.append(severity)
    if anomaly_type:
        filters.append("UPPER(a.anomaly_type) = UPPER(?)")
        params.append(anomaly_type)
        
    where_clause = f"WHERE {' AND '.join(filters)}" if filters else ""
    
    sql = f"""
        SELECT 
            a.anomaly_id,
            a.stock_id,
            c.ticker,
            c.company_name,
            c.sector,
            a.trading_date,
            a.anomaly_type,
            a.severity,
            a.metric_value,
            a.baseline_mean,
            a.z_score,
            a.description,
            a.detected_by,
            a.detected_at
        FROM MARKET_ANOMALIES a
        INNER JOIN COMPANIES c ON a.stock_id = c.stock_id
        {where_clause}
        ORDER BY a.trading_date DESC, a.z_score DESC
        FETCH FIRST {int(limit)} ROWS ONLY
    """
    return fetch_all(sql, tuple(params))

def get_anomaly_summary() -> Dict[str, Any]:
    """Calculate summary statistics of anomalies."""
    sql = """
        SELECT 
            COUNT(*) AS total_anomalies,
            SUM(CASE WHEN severity = 'CRITICAL' THEN 1 ELSE 0 END) AS critical_count,
            SUM(CASE WHEN severity = 'HIGH' THEN 1 ELSE 0 END) AS high_count,
            SUM(CASE WHEN severity = 'MEDIUM' THEN 1 ELSE 0 END) AS medium_count,
            SUM(CASE WHEN severity = 'LOW' THEN 1 ELSE 0 END) AS low_count
        FROM MARKET_ANOMALIES
    """
    row = fetch_one(sql) or {}
    
    type_sql = """
        SELECT anomaly_type, COUNT(*) AS cnt
        FROM MARKET_ANOMALIES
        GROUP BY anomaly_type
    """
    type_rows = fetch_all(type_sql)
    by_type = {r["anomaly_type"]: int(r["cnt"]) for r in type_rows}
    
    return {
        "total_anomalies": int(row.get("total_anomalies") or 0),
        "critical_count": int(row.get("critical_count") or 0),
        "high_count": int(row.get("high_count") or 0),
        "medium_count": int(row.get("medium_count") or 0),
        "low_count": int(row.get("low_count") or 0),
        "by_type": by_type
    }

def run_anomaly_detection_scan(stock_id: Optional[int] = None) -> int:
    """
    Scans price series in Db2, computes statistical rolling baselines,
    and inserts newly identified anomalies into MARKET_ANOMALIES.
    """
    if stock_id:
        companies_sql = "SELECT stock_id, ticker FROM COMPANIES WHERE stock_id = ?"
        companies = fetch_all(companies_sql, (stock_id,))
    else:
        companies_sql = "SELECT stock_id, ticker FROM COMPANIES"
        companies = fetch_all(companies_sql)
    
    total_new_anomalies = 0
    
    for comp in companies:
        sid = comp["stock_id"]
        ticker = comp["ticker"]
        
        # Pull chronological price history
        sql = """
            SELECT price_id, trading_date, open_price, high_price, low_price, close_price, volume, daily_return_pct
            FROM DAILY_PRICES
            WHERE stock_id = ?
            ORDER BY trading_date ASC
        """
        rows = fetch_all(sql, (sid,))
        if len(rows) < 15:
            continue
            
        df = pd.DataFrame(rows)
        df["volume"] = pd.to_numeric(df["volume"], errors="coerce").fillna(0)
        df["daily_return_pct"] = pd.to_numeric(df["daily_return_pct"], errors="coerce").fillna(0)
        df["high_price"] = pd.to_numeric(df["high_price"], errors="coerce")
        df["low_price"] = pd.to_numeric(df["low_price"], errors="coerce")
        
        # 20-day rolling baseline for volume
        df["vol_mean"] = df["volume"].rolling(window=20, min_periods=5).mean()
        df["vol_std"] = df["volume"].rolling(window=20, min_periods=5).std().replace(0, np.nan)
        df["vol_zscore"] = (df["volume"] - df["vol_mean"]) / df["vol_std"]
        
        # 20-day rolling baseline for returns
        df["ret_std"] = df["daily_return_pct"].rolling(window=20, min_periods=5).std().replace(0, np.nan)
        df["ret_mean"] = df["daily_return_pct"].rolling(window=20, min_periods=5).mean()
        df["ret_zscore"] = (df["daily_return_pct"] - df["ret_mean"]) / df["ret_std"]
        
        # Find existing anomalies to prevent duplicate insertions
        existing_sql = "SELECT trading_date, anomaly_type FROM MARKET_ANOMALIES WHERE stock_id = ?"
        existing_rows = fetch_all(existing_sql, (sid,))
        existing_set = {(str(r["trading_date"]), r["anomaly_type"]) for r in existing_rows}
        
        insert_sql = """
            INSERT INTO MARKET_ANOMALIES (
                stock_id, trading_date, anomaly_type, severity, metric_value,
                baseline_mean, z_score, description, detected_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'AnomalyDetectionAgent')
        """
        
        for _, row_data in df.dropna(subset=["vol_zscore"]).iterrows():
            t_date = str(row_data["trading_date"])
            vol_z = float(row_data["vol_zscore"])
            ret_z = float(row_data["ret_zscore"]) if not pd.isna(row_data["ret_zscore"]) else 0.0
            ret_pct = float(row_data["daily_return_pct"])
            vol = float(row_data["volume"])
            vol_avg = float(row_data["vol_mean"])
            
            # 1. Volume Surge check
            if vol_z >= 2.0:
                if (t_date, "VOLUME_SURGE") not in existing_set:
                    severity = "CRITICAL" if vol_z >= 3.5 else ("HIGH" if vol_z >= 2.5 else "MEDIUM")
                    desc = f"Unusual volume surge for {ticker}: {vol:,.0f} shares vs 20d mean of {vol_avg:,.0f} (z-score: {vol_z:.2f})."
                    execute_statement(insert_sql, (sid, t_date, "VOLUME_SURGE", severity, vol, vol_avg, vol_z, desc))
                    existing_set.add((t_date, "VOLUME_SURGE"))
                    total_new_anomalies += 1
                    
            # 2. Extreme Price Spike / Plunge check
            if abs(ret_z) >= 2.2 or abs(ret_pct) >= 4.0:
                if (t_date, "PRICE_SPIKE") not in existing_set:
                    severity = "CRITICAL" if abs(ret_pct) >= 7.0 or abs(ret_z) >= 3.5 else ("HIGH" if abs(ret_pct) >= 4.5 else "MEDIUM")
                    direction = "surge" if ret_pct > 0 else "drop"
                    desc = f"Significant single-day price {direction} of {ret_pct:+.2f}% for {ticker} (z-score: {ret_z:.2f})."
                    execute_statement(insert_sql, (sid, t_date, "PRICE_SPIKE", severity, ret_pct, float(row_data["ret_mean"]), ret_z, desc))
                    existing_set.add((t_date, "PRICE_SPIKE"))
                    total_new_anomalies += 1
                    
            # 3. Intraday Volatility Burst
            if row_data["low_price"] > 0:
                intraday_spread = ((row_data["high_price"] - row_data["low_price"]) / row_data["low_price"]) * 100
                if intraday_spread >= 5.0 and (t_date, "VOLATILITY_BURST") not in existing_set:
                    severity = "HIGH" if intraday_spread >= 8.0 else "MEDIUM"
                    desc = f"Elevated intraday price swing of {intraday_spread:.2f}% (High: ${row_data['high_price']:.2f}, Low: ${row_data['low_price']:.2f})."
                    execute_statement(insert_sql, (sid, t_date, "VOLATILITY_BURST", severity, intraday_spread, None, None, desc))
                    existing_set.add((t_date, "VOLATILITY_BURST"))
                    total_new_anomalies += 1
                    
    return total_new_anomalies

