"""
DRISHTI — Data Ingestion & Sample Market Data Engine
Validates CSV and Excel files, enforces data integrity, prevents duplicates,
and populates realistic seed data in IBM Db2.
"""
import io
import math
import random
from datetime import date, datetime, timedelta
from typing import Dict, Any, List, Tuple
import pandas as pd
import numpy as np

from backend.core.db2 import fetch_all, fetch_one, execute_statement
from backend.services.anomaly_service import run_anomaly_detection_scan
from backend.services.sector_service import recalculate_sector_metrics

REQUIRED_PRICE_COLUMNS = {"ticker", "trading_date", "open_price", "high_price", "low_price", "close_price", "volume"}

def validate_and_ingest_dataframe(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Validates a pandas DataFrame containing market data, inserts/updates companies
    and inserts daily price series into IBM Db2.
    """
    # Normalize column names
    df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]
    
    if df.empty:
        raise ValueError("Uploaded dataset is empty (0 data rows).")
        
    missing = REQUIRED_PRICE_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns in dataset: {sorted(list(missing))}")
        
    errors = []
    inserted_prices = 0
    updated_prices = 0
    new_companies = 0
    
    # Cache existing companies
    comp_rows = fetch_all("SELECT stock_id, ticker FROM COMPANIES")
    company_cache = {r["ticker"].upper(): r["stock_id"] for r in comp_rows}
    
    # Process distinct companies first
    for ticker in df["ticker"].dropna().unique():
        ticker_str = str(ticker).strip().upper()
        if ticker_str not in company_cache:
            # Look for company details in df
            ticker_slice = df[df["ticker"].str.upper() == ticker_str]
            comp_name = ticker_slice["company_name"].iloc[0] if "company_name" in ticker_slice.columns and not pd.isna(ticker_slice["company_name"].iloc[0]) else f"{ticker_str} Corp"
            sector = ticker_slice["sector"].iloc[0] if "sector" in ticker_slice.columns and not pd.isna(ticker_slice["sector"].iloc[0]) else "General"
            industry = ticker_slice["industry"].iloc[0] if "industry" in ticker_slice.columns and not pd.isna(ticker_slice["industry"].iloc[0]) else None
            mcap = float(ticker_slice["market_cap"].iloc[0]) if "market_cap" in ticker_slice.columns and not pd.isna(ticker_slice["market_cap"].iloc[0]) else None
            
            insert_comp_sql = """
                INSERT INTO COMPANIES (ticker, company_name, sector, industry, market_cap)
                VALUES (?, ?, ?, ?, ?)
            """
            execute_statement(insert_comp_sql, (ticker_str, comp_name, sector, industry, mcap))
            new_companies += 1
            
            # Refresh ID
            chk = fetch_one("SELECT stock_id FROM COMPANIES WHERE ticker = ?", (ticker_str,))
            if chk:
                company_cache[ticker_str] = chk["stock_id"]
                
    # Sort dataframe by ticker and date for return calculations
    df["trading_date"] = pd.to_datetime(df["trading_date"]).dt.date
    df = df.sort_values(by=["ticker", "trading_date"])
    
    # Ingest prices
    for idx, row in df.iterrows():
        try:
            ticker_str = str(row["ticker"]).strip().upper()
            stock_id = company_cache.get(ticker_str)
            if not stock_id:
                continue
                
            t_date = row["trading_date"]
            open_p = float(row["open_price"])
            high_p = float(row["high_price"])
            low_p = float(row["low_price"])
            close_p = float(row["close_price"])
            vol = int(row["volume"])
            
            # Validation rules
            if open_p <= 0 or high_p <= 0 or low_p <= 0 or close_p <= 0:
                errors.append(f"Row {idx}: Non-positive prices encountered.")
                continue
            if high_p < low_p:
                errors.append(f"Row {idx}: High price {high_p} is less than Low price {low_p}.")
                continue
            if vol < 0:
                errors.append(f"Row {idx}: Negative volume encountered.")
                continue
                
            vwap = round((open_p + high_p + low_p + close_p) / 4.0, 4)
            
            # Calculate return if not provided
            ret_pct = None
            if "daily_return_pct" in row and not pd.isna(row["daily_return_pct"]):
                ret_pct = float(row["daily_return_pct"])
            elif open_p > 0:
                ret_pct = round(((close_p - open_p) / open_p) * 100, 4)
                
            # Check duplicate (stock_id, trading_date)
            chk_price_sql = "SELECT price_id FROM DAILY_PRICES WHERE stock_id = ? AND trading_date = ?"
            existing_price = fetch_one(chk_price_sql, (stock_id, t_date))
            
            if existing_price:
                update_sql = """
                    UPDATE DAILY_PRICES
                    SET open_price = ?, high_price = ?, low_price = ?, close_price = ?,
                        volume = ?, vwap = ?, daily_return_pct = ?
                    WHERE price_id = ?
                """
                execute_statement(update_sql, (open_p, high_p, low_p, close_p, vol, vwap, ret_pct, existing_price["price_id"]))
                updated_prices += 1
            else:
                insert_price_sql = """
                    INSERT INTO DAILY_PRICES (
                        stock_id, trading_date, open_price, high_price, low_price,
                        close_price, volume, vwap, daily_return_pct
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                execute_statement(insert_price_sql, (stock_id, t_date, open_p, high_p, low_p, close_p, vol, vwap, ret_pct))
                inserted_prices += 1
        except Exception as e:
            errors.append(f"Row {idx}: {str(e)}")
            
    # Run analytical rollups
    anomalies_detected = run_anomaly_detection_scan()
    recalculate_sector_metrics()
    
    return {
        "status": "success",
        "new_companies_created": new_companies,
        "prices_inserted": inserted_prices,
        "prices_updated": updated_prices,
        "anomalies_detected": anomalies_detected,
        "errors_encountered": errors[:10]  # capped for clean reporting
    }

def seed_sample_market_data() -> Dict[str, Any]:
    """
    Seeds DRISHTI with 6 realistic market leaders across diverse sectors
    with 90 trading days of historical data, including authentic volume anomalies.
    """
    SAMPLE_STOCKS = [
        {"ticker": "AAPL", "name": "Apple Inc.", "sector": "Technology", "industry": "Consumer Electronics", "cap": 3450000000000, "base_price": 225.0, "base_vol": 45000000},
        {"ticker": "NVDA", "name": "NVIDIA Corporation", "sector": "Technology", "industry": "Semiconductors", "cap": 3100000000000, "base_price": 128.0, "base_vol": 60000000},
        {"ticker": "MSFT", "name": "Microsoft Corporation", "sector": "Technology", "industry": "Software", "cap": 3200000000000, "base_price": 420.0, "base_vol": 22000000},
        {"ticker": "JPM", "name": "JPMorgan Chase & Co.", "sector": "Financials", "industry": "Diversified Banking", "cap": 620000000000, "base_price": 218.0, "base_vol": 9500000},
        {"ticker": "JNJ", "name": "Johnson & Johnson", "sector": "Healthcare", "industry": "Pharmaceuticals", "cap": 380000000000, "base_price": 158.0, "base_vol": 7800000},
        {"ticker": "XOM", "name": "Exxon Mobil Corporation", "sector": "Energy", "industry": "Integrated Oil & Gas", "cap": 490000000000, "base_price": 116.0, "base_vol": 14000000},
    ]
    
    rows = []
    # Seed 90 days backwards ending yesterday
    end_dt = date.today() - timedelta(days=1)
    
    random.seed(42)  # Deterministic seed for reproducible evaluation
    
    for s in SAMPLE_STOCKS:
        price = s["base_price"]
        curr_dt = end_dt - timedelta(days=130)
        
        while curr_dt <= end_dt:
            # Skip weekends
            if curr_dt.weekday() < 5:
                # Normal market noise
                change_pct = random.gauss(0.0008, 0.015)
                vol_mult = random.uniform(0.7, 1.4)
                
                # Introduce realistic market shock events (earnings, breakouts)
                # Apple earnings shock on day 45
                if s["ticker"] == "AAPL" and curr_dt == end_dt - timedelta(days=45):
                    change_pct = 0.068  # +6.8%
                    vol_mult = 3.8     # Massive volume spike
                # Nvidia AI chip announcement on day 20
                elif s["ticker"] == "NVDA" and curr_dt == end_dt - timedelta(days=20):
                    change_pct = 0.092  # +9.2%
                    vol_mult = 4.2     # Critical volume surge
                # JPMorgan credit provisions surprise on day 60
                elif s["ticker"] == "JPM" and curr_dt == end_dt - timedelta(days=60):
                    change_pct = -0.054 # -5.4% selloff
                    vol_mult = 3.2
                # Exxon crude spike on day 12
                elif s["ticker"] == "XOM" and curr_dt == end_dt - timedelta(days=12):
                    change_pct = 0.048
                    vol_mult = 3.1
                    
                open_p = round(price * (1 + random.uniform(-0.003, 0.003)), 2)
                close_p = round(price * (1 + change_pct), 2)
                high_p = round(max(open_p, close_p) * (1 + random.uniform(0.002, 0.012)), 2)
                low_p = round(min(open_p, close_p) * (1 - random.uniform(0.002, 0.012)), 2)
                volume = int(s["base_vol"] * vol_mult)
                ret_pct = round(((close_p - open_p) / open_p) * 100, 4)
                
                rows.append({
                    "ticker": s["ticker"],
                    "company_name": s["name"],
                    "sector": s["sector"],
                    "industry": s["industry"],
                    "market_cap": s["cap"],
                    "trading_date": curr_dt,
                    "open_price": open_p,
                    "high_price": high_p,
                    "low_price": low_p,
                    "close_price": close_p,
                    "volume": volume,
                    "daily_return_pct": ret_pct
                })
                price = close_p
            curr_dt += timedelta(days=1)
            
    df = pd.DataFrame(rows)
    return validate_and_ingest_dataframe(df)

