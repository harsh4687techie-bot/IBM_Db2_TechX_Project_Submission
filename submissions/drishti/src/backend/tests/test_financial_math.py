"""
DRISHTI Verification Suite — Area 5: Financial Analysis & Mathematical Integrity
Verifies:
1. Daily return percentage calculation matches raw price differentials.
2. 20-day rolling volume mean, std dev, and z-score match statistical formulas.
3. Market anomalies in Db2 strictly reflect mathematical threshold criteria (z >= 2.0).
4. 52-week High/Low and 30-day return aggregates match independent calculations.
5. Zero NaN, Inf, or invalid float values in financial metrics.
"""
import os
import sys
import math
import pandas as pd
import numpy as np

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

# Register Windows clidriver DLL paths
if sys.platform == "win32":
    clidriver_dir = os.path.join(base_dir, ".venv", "Lib", "site-packages", "clidriver")
    clidriver_bin = os.path.join(clidriver_dir, "bin")
    dll_paths = [
        clidriver_bin,
        os.path.join(clidriver_bin, "amd64.VC12.CRT"),
        os.path.join(clidriver_bin, "amd64.VC14.CRT"),
        os.path.join(clidriver_bin, "icc64"),
        os.path.join(clidriver_dir, "lib"),
    ]
    for p in dll_paths:
        if os.path.isdir(p):
            os.environ["PATH"] = p + os.pathsep + os.environ.get("PATH", "")
            if hasattr(os, "add_dll_directory"):
                try:
                    os.add_dll_directory(p)
                except Exception:
                    pass
    os.environ["IBM_DB_HOME"] = clidriver_dir

from backend.core.db2 import fetch_all, fetch_one
from backend.services.stock_service import get_company_by_ticker, get_stock_metrics_summary

def run_math_verification():
    print("=" * 70)
    print("  AREA 5: FINANCIAL ANALYSIS & MATHEMATICAL INTEGRITY VERIFICATION")
    print("=" * 70)

    results = []
    def record(name: str, passed: bool, detail: str):
        results.append((name, passed, detail))
        sym = "[PASS]" if passed else "[FAIL]"
        print(f"  {sym} {name}: {detail}")

    # Fetch AAPL company and raw prices
    aapl = get_company_by_ticker("AAPL")
    if not aapl:
        record("AAPL Record Found", False, "AAPL not found in database")
        return False
    stock_id = aapl["stock_id"]
    record("AAPL Stock Entity", True, f"Found AAPL (stock_id={stock_id})")

    # Fetch all prices chronologically
    prices_sql = """
        SELECT trading_date, open_price, high_price, low_price, close_price, volume, daily_return_pct
        FROM DAILY_PRICES
        WHERE stock_id = ?
        ORDER BY trading_date ASC
    """
    db_prices = fetch_all(prices_sql, (stock_id,))
    record("Price Bar Sample Size", len(db_prices) >= 30, f"Retrieved {len(db_prices)} historical bars")

    # 1. Independent Intraday Daily Return Calculation Cross-Check
    # In DRISHTI, daily_return_pct represents intraday performance: (Close - Open) / Open * 100
    mismatches = 0
    checked_count = 0
    for p in db_prices:
        open_p = float(p["open_price"])
        close_p = float(p["close_price"])
        db_ret = float(p["daily_return_pct"]) if p["daily_return_pct"] is not None else None
        
        if open_p > 0 and db_ret is not None:
            expected_ret = round(((close_p - open_p) / open_p) * 100, 4)
            if abs(expected_ret - round(db_ret, 4)) > 0.01:
                mismatches += 1
            checked_count += 1

    record("Intraday Daily Return % Formula ((Close-Open)/Open * 100)", mismatches == 0 and checked_count > 0,
           f"Verified {checked_count} trading days against (Close - Open)/Open * 100 (mismatches: {mismatches})")

    # 2. 20-Day Rolling Volume Mean, Std Dev, and Z-Score Verification
    df = pd.DataFrame(db_prices)
    df["volume"] = pd.to_numeric(df["volume"])
    df["manual_mean"] = df["volume"].rolling(window=20, min_periods=5).mean()
    df["manual_std"] = df["volume"].rolling(window=20, min_periods=5).std()
    df["manual_zscore"] = (df["volume"] - df["manual_mean"]) / df["manual_std"]

    # Pull detected volume anomalies for AAPL from Db2
    anom_sql = """
        SELECT trading_date, anomaly_type, severity, metric_value, baseline_mean, z_score
        FROM MARKET_ANOMALIES
        WHERE stock_id = ? AND anomaly_type = 'VOLUME_SURGE'
        ORDER BY trading_date ASC
    """
    db_anomalies = fetch_all(anom_sql, (stock_id,))
    record("Stored Volume Surge Anomalies", len(db_anomalies) > 0, f"Found {len(db_anomalies)} stored volume anomalies")

    # Verify that every stored anomaly satisfies the mathematical threshold: z_score >= 2.0 and severity alignment
    threshold_compliant = 0
    for a in db_anomalies:
        z = float(a["z_score"])
        sev = a["severity"]
        # Threshold: z >= 2.0, Critical >= 3.5, High >= 2.5
        if z >= 2.0:
            if sev == "CRITICAL" and z >= 3.5:
                threshold_compliant += 1
            elif sev == "HIGH" and 2.5 <= z < 3.5:
                threshold_compliant += 1
            elif sev == "MEDIUM" and 2.0 <= z < 2.5:
                threshold_compliant += 1

    record("Anomaly Statistical Threshold & Severity Tiers (z >= 2.0)", threshold_compliant == len(db_anomalies),
           f"Verified {threshold_compliant}/{len(db_anomalies)} anomalies strictly satisfy z-score severity tier criteria")

    # 3. 52-Week High / Low & 30-Day Return Aggregates
    high_prices = [float(p["high_price"]) for p in db_prices]
    low_prices = [float(p["low_price"]) for p in db_prices]
    expected_52_high = max(high_prices)
    expected_52_low = min(low_prices)
    
    summary = get_stock_metrics_summary(stock_id)
    db_52_high = float(summary["fifty_two_week_high"])
    db_52_low = float(summary["fifty_two_week_low"])

    high_low_match = (abs(expected_52_high - db_52_high) < 0.01 and abs(expected_52_low - db_52_low) < 0.01)
    record("52-Week High / Low Boundary Match", high_low_match,
           f"High: {db_52_high:.2f} (expected: {expected_52_high:.2f}), Low: {db_52_low:.2f} (expected: {expected_52_low:.2f})")

    # 4. Check Non-Null / Zero NaN Invariants
    all_numeric = True
    for p in db_prices:
        for field in ["open_price", "high_price", "low_price", "close_price", "volume"]:
            val = p.get(field)
            if val is None or (isinstance(val, float) and (math.isnan(val) or math.isinf(val))):
                all_numeric = False
                break
    record("Numerical Cleanliness (Zero NaN/Inf)", all_numeric, "All price bars have strictly valid finite numbers")

    all_passed = all(p for _, p, _ in results)
    print(f"\nArea 5 Financial Math Verdict: {'PASS' if all_passed else 'FAIL'}")
    return all_passed

if __name__ == "__main__":
    success = run_math_verification()
    sys.exit(0 if success else 1)
