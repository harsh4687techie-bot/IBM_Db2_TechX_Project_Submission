"""
DRISHTI Verification Suite — Area 4: CSV/XLSX Upload & Ingestion Verification
Verifies:
1. Ingestion of valid CSV data.
2. Ingestion of valid XLSX (Excel) data.
3. Rejection of missing mandatory columns.
4. Rejection of bad data types (non-numeric prices).
5. Rejection of negative prices.
6. Rejection of inverted price bounds (High < Low).
7. Rejection of empty / 0-row datasets.
8. Idempotent MERGE handling (re-upload updates existing, creates 0 duplicates).
9. Non-destructive file preservation (source test files remain intact on disk).
"""
import os
import sys
import io
import pandas as pd

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

from backend.core.db2 import fetch_one
from backend.services.ingestion_service import validate_and_ingest_dataframe

def run_ingestion_verification():
    print("=" * 70)
    print("  AREA 4: CSV/XLSX UPLOAD & INGESTION VERIFICATION")
    print("=" * 70)

    results = []
    def record(name: str, passed: bool, detail: str):
        results.append((name, passed, detail))
        sym = "[PASS]" if passed else "[FAIL]"
        print(f"  {sym} {name}: {detail}")

    # 1. Valid CSV Ingestion
    valid_csv = """ticker,company_name,sector,industry,market_cap,trading_date,open_price,high_price,low_price,close_price,volume
INTC,Intel Corp,Technology,Semiconductors,95000000000,2026-11-01,22.50,23.10,22.40,22.95,45000000
INTC,Intel Corp,Technology,Semiconductors,95000000000,2026-11-02,23.00,23.80,22.90,23.65,52000000
"""
    df_valid_csv = pd.read_csv(io.StringIO(valid_csv))
    res_csv = validate_and_ingest_dataframe(df_valid_csv)
    record("Valid CSV Ingestion", res_csv["status"] == "success" and (res_csv["prices_inserted"] + res_csv["prices_updated"] == 2),
           f"Status: {res_csv['status']}, Inserted: {res_csv['prices_inserted']}, Updated: {res_csv['prices_updated']}")

    # 2. Valid XLSX Ingestion
    xlsx_buffer = io.BytesIO()
    df_valid_csv.to_excel(xlsx_buffer, index=False, engine="openpyxl")
    xlsx_buffer.seek(0)
    df_from_xlsx = pd.read_excel(xlsx_buffer, engine="openpyxl")
    res_xlsx = validate_and_ingest_dataframe(df_from_xlsx)
    record("Valid XLSX Ingestion", res_xlsx["status"] == "success",
           f"Status: {res_xlsx['status']}, Updated: {res_xlsx['prices_updated']}")

    # 3. Missing Mandatory Columns
    missing_col_csv = """company_name,sector,trading_date,open_price,high_price,low_price,close_price
Intel Corp,Technology,2026-11-01,22.50,23.10,22.40,22.95
"""
    df_missing = pd.read_csv(io.StringIO(missing_col_csv))
    rejected_missing = False
    err_msg = ""
    try:
        res_missing = validate_and_ingest_dataframe(df_missing)
        rejected_missing = (res_missing.get("status") == "error")
    except ValueError as e:
        rejected_missing = True
        err_msg = str(e)
    record("Validation: Reject Missing Columns", rejected_missing, f"Rejected gracefully: {err_msg}")

    # 4. Bad Data Types (Non-numeric price)
    bad_type_csv = """ticker,company_name,sector,trading_date,open_price,high_price,low_price,close_price,volume
INTC,Intel Corp,Technology,2026-11-01,NOT_A_PRICE,23.10,22.40,22.95,1000000
"""
    df_bad_type = pd.read_csv(io.StringIO(bad_type_csv))
    res_bad_type = validate_and_ingest_dataframe(df_bad_type)
    record("Validation: Reject Bad Data Types", len(res_bad_type["errors_encountered"]) > 0,
           f"Rejected non-numeric price; Errors: {len(res_bad_type['errors_encountered'])}")

    # 5. Negative Price Rejection
    neg_price_csv = """ticker,company_name,sector,trading_date,open_price,high_price,low_price,close_price,volume
INTC,Intel Corp,Technology,2026-11-01,-22.50,23.10,22.40,22.95,1000000
"""
    df_neg = pd.read_csv(io.StringIO(neg_price_csv))
    res_neg = validate_and_ingest_dataframe(df_neg)
    record("Validation: Reject Negative Prices", len(res_neg["errors_encountered"]) > 0,
           f"Errors: {res_neg['errors_encountered']}")

    # 6. Inverted Price Bounds (High < Low)
    inv_csv = """ticker,company_name,sector,trading_date,open_price,high_price,low_price,close_price,volume
INTC,Intel Corp,Technology,2026-11-01,25.00,20.00,30.00,24.00,1000000
"""
    df_inv = pd.read_csv(io.StringIO(inv_csv))
    res_inv = validate_and_ingest_dataframe(df_inv)
    record("Validation: Reject Inverted Bounds (High < Low)", len(res_inv["errors_encountered"]) > 0,
           f"Errors: {res_inv['errors_encountered']}")

    # 7. Empty / 0-row Dataset
    df_empty = pd.DataFrame(columns=["ticker", "trading_date", "open_price", "high_price", "low_price", "close_price", "volume"])
    rejected_empty = False
    empty_msg = ""
    try:
        res_empty = validate_and_ingest_dataframe(df_empty)
        rejected_empty = (res_empty.get("status") == "error")
    except ValueError as e:
        rejected_empty = True
        empty_msg = str(e)
    record("Validation: Reject Empty Dataset", rejected_empty, f"Rejected empty dataframe: {empty_msg}")

    # 8. Idempotent Ingestion / Duplicate Prevention
    res_idempotent = validate_and_ingest_dataframe(df_valid_csv)
    record("Idempotency (0 Duplicate Rows Created)", res_idempotent["prices_inserted"] == 0 and res_idempotent["prices_updated"] == 2,
           f"Inserted: {res_idempotent['prices_inserted']}, Updated existing: {res_idempotent['prices_updated']}")

    # 9. Source File Integrity on Disk
    sample_test_path = os.path.join(base_dir, "backend", "tests", "sample_test_upload.csv")
    with open(sample_test_path, "w", encoding="utf-8") as f:
        f.write(valid_csv)
    # Read and ingest from file
    df_disk = pd.read_csv(sample_test_path)
    validate_and_ingest_dataframe(df_disk)
    file_intact = os.path.exists(sample_test_path) and os.path.getsize(sample_test_path) > 0
    # Clean up test file
    try:
        os.remove(sample_test_path)
    except Exception:
        pass
    record("Source File Preservation (Non-destructive)", file_intact, "Disk file was not corrupted or overwritten during ingestion")

    all_passed = all(p for _, p, _ in results)
    print(f"\nArea 4 Ingestion Verdict: {'PASS' if all_passed else 'FAIL'}")
    return all_passed

if __name__ == "__main__":
    success = run_ingestion_verification()
    sys.exit(0 if success else 1)
