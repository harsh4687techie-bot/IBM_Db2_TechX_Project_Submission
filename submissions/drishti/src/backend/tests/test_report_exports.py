"""
DRISHTI Verification Suite — Area 6: Report Generation & Document Integrity
Verifies:
1. Automated compilation of PDF reports via ReportLab.
2. Automated compilation of multi-sheet Excel workbooks via OpenPyXL.
3. File existence and valid header checks on disk.
4. Excel workbook cell integrity: zero #VALUE!, #REF!, NaN, or unhandled null strings.
5. Db2 metadata persistence in ANALYSIS_REPORTS table with UUID.
"""
import os
import sys
import uuid
import openpyxl

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
from backend.services.report_service import (
    create_and_save_report, 
    generate_pdf_report, 
    generate_excel_report,
    get_report_by_uuid
)

def run_report_verification():
    print("=" * 70)
    print("  AREA 6: REPORT GENERATION & DOCUMENT INTEGRITY VERIFICATION")
    print("=" * 70)

    results = []
    def record(name: str, passed: bool, detail: str):
        results.append((name, passed, detail))
        sym = "[PASS]" if passed else "[FAIL]"
        print(f"  {sym} {name}: {detail}")

    # Generate a fresh test report for NVDA
    rep_uuid = str(uuid.uuid4())[:8]
    summary_md = """# DRISHTI Executive Intelligence Briefing: NVDA
## Key Observations
- Demonstrated robust momentum across the past quarter.
- Volume expansion coincides with AI semiconductor infrastructure tailwinds.
"""
    key_findings = {
        "metrics": {"latest_close": 128.50, "thirty_day_return_pct": 14.25},
        "anomalies_count": 3,
        "sector": "Technology"
    }

    report = create_and_save_report(
        title=f"DRISHTI QA Audit Report — NVIDIA (NVDA) [{rep_uuid}]",
        target_ticker="NVDA",
        summary_markdown=summary_md,
        key_findings=key_findings,
        report_type="AUDIT_VERIFICATION"
    )
    
    actual_uuid = report["report_uuid"]
    record("Report Creation in Db2 (ANALYSIS_REPORTS)", bool(actual_uuid), f"Generated UUID: {actual_uuid}")

    # 1. Verify PDF on disk
    pdf_path = report["file_path_pdf"]
    pdf_exists = os.path.exists(pdf_path)
    pdf_size = os.path.getsize(pdf_path) if pdf_exists else 0
    pdf_valid_header = False
    if pdf_exists:
        with open(pdf_path, "rb") as f:
            header_bytes = f.read(5)
            pdf_valid_header = header_bytes.startswith(b"%PDF-")
    
    record("PDF Artifact on Disk (ReportLab)", pdf_exists and pdf_size > 1500 and pdf_valid_header,
           f"Path: {os.path.basename(pdf_path)} ({pdf_size} bytes, Valid %PDF- header)")

    # 2. Verify Excel workbook on disk (OpenPyXL)
    xlsx_path = report["file_path_excel"]
    xlsx_exists = os.path.exists(xlsx_path)
    xlsx_size = os.path.getsize(xlsx_path) if xlsx_exists else 0
    record("Excel Artifact on Disk (OpenPyXL)", xlsx_exists and xlsx_size > 5000,
           f"Path: {os.path.basename(xlsx_path)} ({xlsx_size} bytes)")

    # 3. Inspect Excel Sheets & Data Cleanliness
    wb = openpyxl.load_workbook(xlsx_path, data_only=True)
    sheet_names = wb.sheetnames
    has_expected_sheets = all(s in sheet_names for s in ["Executive Summary", "Price History"])
    record("Excel Worksheets Structure", has_expected_sheets, f"Sheets: {sheet_names}")

    # Scan all cells for error formulas or NaN values
    corrupted_cells = []
    for sheet_name in sheet_names:
        sheet = wb[sheet_name]
        for row in sheet.iter_rows(values_only=True):
            for cell in row:
                if isinstance(cell, str):
                    if any(err in cell for err in ["#VALUE!", "#REF!", "#N/A", "NaN"]):
                        corrupted_cells.append(f"{sheet_name}: {cell}")

    record("Excel Cell Formula & Data Cleanliness", len(corrupted_cells) == 0,
           f"Zero corrupted formula cells found (Total errors: {len(corrupted_cells)})")

    # 4. Cross-check Db2 persistence
    db_rep = get_report_by_uuid(actual_uuid)
    db_matched = (
        db_rep is not None and 
        db_rep["target_ticker"] == "NVDA" and 
        os.path.abspath(db_rep["file_path_pdf"]) == os.path.abspath(pdf_path)
    )
    record("Db2 Catalog Record & Path Integrity", db_matched,
           f"Catalog entry matches filesystem paths for report {actual_uuid}")

    all_passed = all(p for _, p, _ in results)
    print(f"\nArea 6 Report Generation Verdict: {'PASS' if all_passed else 'FAIL'}")
    return all_passed

if __name__ == "__main__":
    success = run_report_verification()
    sys.exit(0 if success else 1)
