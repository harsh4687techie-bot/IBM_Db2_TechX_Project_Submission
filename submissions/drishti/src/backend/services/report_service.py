"""
DRISHTI — Executive Report Generation Service
Generates professional PDF and Excel financial intelligence reports and tracks them in Db2.
"""
import os
import uuid
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

from backend.core.config import settings
from backend.core.db2 import execute_statement, fetch_all, fetch_one
from backend.services.stock_service import get_company_by_ticker, get_stock_price_history, get_stock_metrics_summary
from backend.services.anomaly_service import get_anomalies

settings.EXPORTS_DIR.mkdir(parents=True, exist_ok=True)

def generate_excel_report(ticker: str, report_uuid: str) -> str:
    """Generates a styled financial analysis workbook using openpyxl."""
    comp = get_company_by_ticker(ticker)
    if not comp:
        raise ValueError(f"Stock '{ticker}' not found.")
        
    prices = get_stock_price_history(comp["stock_id"], limit=90)
    anomalies = get_anomalies(stock_id=comp["stock_id"], limit=50)
    metrics = get_stock_metrics_summary(comp["stock_id"])
    
    wb = openpyxl.Workbook()
    ws_summary = wb.active
    ws_summary.title = "Executive Summary"
    
    # Styles
    navy_fill = PatternFill(start_color="0F172A", end_color="0F172A", fill_type="solid")
    header_fill = PatternFill(start_color="1E293B", end_color="1E293B", fill_type="solid")
    accent_fill = PatternFill(start_color="3B82F6", end_color="3B82F6", fill_type="solid")
    white_bold = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    title_font = Font(name="Calibri", size=16, bold=True, color="FFFFFF")
    bold_font = Font(name="Calibri", size=11, bold=True)
    
    # Header block
    ws_summary.merge_cells("A1:F1")
    cell = ws_summary["A1"]
    cell.value = f"DRISHTI INTELLIGENCE REPORT — {comp['company_name']} ({comp['ticker']})"
    cell.font = title_font
    cell.fill = navy_fill
    cell.alignment = Alignment(horizontal="center", vertical="center")
    ws_summary.row_dimensions[1].height = 40
    
    # Metadata
    mcap = float(comp.get("market_cap") or 0)
    ret_30d = float(metrics.get("thirty_day_return_pct") or 0)
    h52 = float(metrics.get("fifty_two_week_high") or 0)
    l52 = float(metrics.get("fifty_two_week_low") or 0)
    metadata = [
        ("Sector", comp.get("sector", "N/A"), "Generated At", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        ("Industry", comp.get("industry", "N/A"), "Report UUID", report_uuid),
        ("Market Cap", f"${mcap:,.2f}", "30-Day Return", f"{ret_30d:+.2f}%"),
        ("52-Week High", f"${h52:,.2f}", "52-Week Low", f"${l52:,.2f}"),
    ]
    
    r_idx = 3
    for label1, val1, label2, val2 in metadata:
        ws_summary.cell(row=r_idx, column=1, value=label1).font = bold_font
        ws_summary.cell(row=r_idx, column=2, value=val1)
        ws_summary.cell(row=r_idx, column=4, value=label2).font = bold_font
        ws_summary.cell(row=r_idx, column=5, value=val2)
        r_idx += 1
        
    # Anomaly Section
    r_idx += 2
    ws_summary.cell(row=r_idx, column=1, value="Detected Market Anomalies").font = Font(size=14, bold=True)
    r_idx += 1
    
    anom_headers = ["Date", "Type", "Severity", "Metric Value", "Baseline Mean", "Z-Score", "Description"]
    for c_idx, h in enumerate(anom_headers, start=1):
        c = ws_summary.cell(row=r_idx, column=c_idx, value=h)
        c.font = white_bold
        c.fill = header_fill
        
    for a in anomalies:
        r_idx += 1
        ws_summary.cell(row=r_idx, column=1, value=str(a.get("trading_date")))
        ws_summary.cell(row=r_idx, column=2, value=a.get("anomaly_type"))
        ws_summary.cell(row=r_idx, column=3, value=a.get("severity"))
        ws_summary.cell(row=r_idx, column=4, value=f"{float(a.get('metric_value') or 0):,.2f}")
        ws_summary.cell(row=r_idx, column=5, value=f"{float(a.get('baseline_mean') or 0):,.2f}")
        ws_summary.cell(row=r_idx, column=6, value=round(float(a.get("z_score") or 0), 2))
        ws_summary.cell(row=r_idx, column=7, value=a.get("description"))
        
    # Price History Sheet
    ws_prices = wb.create_sheet(title="Price History")
    p_headers = ["Trading Date", "Open", "High", "Low", "Close", "Volume", "Daily Return %"]
    for c_idx, h in enumerate(p_headers, start=1):
        c = ws_prices.cell(row=1, column=c_idx, value=h)
        c.font = white_bold
        c.fill = header_fill
        
    for idx, p in enumerate(reversed(prices), start=2):
        ws_prices.cell(row=idx, column=1, value=str(p.get("trading_date")))
        ws_prices.cell(row=idx, column=2, value=float(p.get("open_price") or 0))
        ws_prices.cell(row=idx, column=3, value=float(p.get("high_price") or 0))
        ws_prices.cell(row=idx, column=4, value=float(p.get("low_price") or 0))
        ws_prices.cell(row=idx, column=5, value=float(p.get("close_price") or 0))
        ws_prices.cell(row=idx, column=6, value=int(p.get("volume") or 0))
        ws_prices.cell(row=idx, column=7, value=float(p.get("daily_return_pct") or 0))
        
    # Auto-adjust column widths
    for sheet in [ws_summary, ws_prices]:
        for col in sheet.columns:
            max_len = max(len(str(c.value or "")) for c in col)
            col_letter = openpyxl.utils.get_column_letter(col[0].column)
            sheet.column_dimensions[col_letter].width = max(max_len + 3, 12)
            
    file_name = f"drishti_report_{ticker}_{report_uuid[:8]}.xlsx"
    file_path = settings.EXPORTS_DIR / file_name
    wb.save(file_path)
    return str(file_path)

def generate_pdf_report(ticker: str, report_uuid: str, narrative_markdown: str) -> str:
    """Generates an executive PDF report using ReportLab."""
    comp = get_company_by_ticker(ticker)
    if not comp:
        raise ValueError(f"Stock '{ticker}' not found.")
        
    file_name = f"drishti_report_{ticker}_{report_uuid[:8]}.pdf"
    file_path = settings.EXPORTS_DIR / file_name
    
    doc = SimpleDocTemplate(
        str(file_path),
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Heading1"],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#0F172A")
    )
    subtitle_style = ParagraphStyle(
        "Subtitle",
        parent=styles["Normal"],
        fontSize=11,
        textColor=colors.HexColor("#64748B"),
        spaceAfter=15
    )
    body_style = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#1E293B"),
        spaceAfter=10
    )
    
    story = []
    story.append(Paragraph(f"DRISHTI — Financial Intelligence Report", title_style))
    story.append(Paragraph(f"Company: {comp['company_name']} ({comp['ticker']}) | Sector: {comp['sector']} | Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", subtitle_style))
    story.append(Spacer(1, 10))
    
    # Narrative paragraphs
    for line in narrative_markdown.split("\n"):
        line = line.strip()
        if not line:
            continue
        if line.startswith("#"):
            h_text = line.lstrip("#").strip()
            story.append(Paragraph(f"<b>{h_text}</b>", styles["Heading2"]))
        else:
            story.append(Paragraph(line, body_style))
            
    doc.build(story)
    return str(file_path)

def create_and_save_report(
    title: str,
    target_ticker: str,
    summary_markdown: str,
    key_findings: Optional[Dict[str, Any]] = None,
    report_type: str = "STOCK_DEEP_DIVE"
) -> Dict[str, Any]:
    """Generates PDF and Excel files, then records the report in IBM Db2."""
    rep_uuid = str(uuid.uuid4())
    
    # Generate files
    excel_path = generate_excel_report(target_ticker, rep_uuid)
    pdf_path = generate_pdf_report(target_ticker, rep_uuid, summary_markdown)
    
    findings_json = json.dumps(key_findings or {}, default=str)
    
    insert_sql = """
        INSERT INTO ANALYSIS_REPORTS (
            report_uuid, report_title, target_ticker, report_type,
            summary_markdown, key_findings_json, file_path_pdf,
            file_path_excel, generated_by
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'ReportGenerationAgent')
    """
    execute_statement(
        insert_sql,
        (
            rep_uuid,
            title,
            target_ticker,
            report_type,
            summary_markdown,
            findings_json,
            pdf_path,
            excel_path
        )
    )
    
    return {
        "report_uuid": rep_uuid,
        "title": title,
        "ticker": target_ticker,
        "report_type": report_type,
        "file_path_pdf": pdf_path,
        "file_path_excel": excel_path,
        "created_at": datetime.now().isoformat()
    }

def get_report_by_uuid(report_uuid: str) -> Optional[Dict[str, Any]]:
    """Retrieve report metadata by UUID."""
    sql = """
        SELECT report_id, report_uuid, report_title, target_ticker, report_type,
               summary_markdown, key_findings_json, file_path_pdf, file_path_excel,
               generated_by, created_at
        FROM ANALYSIS_REPORTS
        WHERE report_uuid = ?
    """
    return fetch_one(sql, (report_uuid,))

def get_all_reports(limit: int = 20) -> List[Dict[str, Any]]:
    """List recent reports."""
    sql = f"""
        SELECT report_id, report_uuid, report_title, target_ticker, report_type,
               file_path_pdf, file_path_excel, generated_by, created_at
        FROM ANALYSIS_REPORTS
        ORDER BY created_at DESC
        FETCH FIRST {int(limit)} ROWS ONLY
    """
    return fetch_all(sql)

