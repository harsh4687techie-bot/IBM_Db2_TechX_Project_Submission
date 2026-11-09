"""
DRISHTI — Reports API Router
Serves executive markdown reports and binary PDF/Excel downloads.
"""
from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from backend.services.report_service import (
    get_all_reports,
    get_report_by_uuid,
    create_and_save_report
)
from backend.models.report import ReportCreateRequest

router = APIRouter(prefix="/api/reports", tags=["Reports"])

@router.get("")
def list_reports():
    """List recent analytical intelligence reports."""
    return get_all_reports()

@router.get("/{report_uuid}")
def get_report(report_uuid: str):
    """Retrieve full report metadata and markdown narrative."""
    rep = get_report_by_uuid(report_uuid)
    if not rep:
        raise HTTPException(status_code=404, detail="Report not found.")
    return rep

@router.get("/{report_uuid}/pdf")
def download_pdf(report_uuid: str):
    """Download the executive PDF report."""
    rep = get_report_by_uuid(report_uuid)
    if not rep or not rep.get("file_path_pdf"):
        raise HTTPException(status_code=404, detail="Report PDF not found.")
        
    pdf_path = Path(rep["file_path_pdf"])
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail="PDF artifact missing on disk.")
        
    return FileResponse(
        path=pdf_path,
        filename=pdf_path.name,
        media_type="application/pdf"
    )

@router.get("/{report_uuid}/excel")
def download_excel(report_uuid: str):
    """Download the analytical Excel workbook."""
    rep = get_report_by_uuid(report_uuid)
    if not rep or not rep.get("file_path_excel"):
        raise HTTPException(status_code=404, detail="Report Excel workbook not found.")
        
    xlsx_path = Path(rep["file_path_excel"])
    if not xlsx_path.exists():
        raise HTTPException(status_code=404, detail="Excel artifact missing on disk.")
        
    return FileResponse(
        path=xlsx_path,
        filename=xlsx_path.name,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

@router.post("")
def generate_custom_report(req: ReportCreateRequest):
    """Manually generate and persist an executive report."""
    if not req.target_ticker:
        raise HTTPException(status_code=400, detail="Target ticker symbol is required.")
        
    result = create_and_save_report(
        title=req.report_title,
        target_ticker=req.target_ticker,
        summary_markdown=req.summary_markdown,
        key_findings=req.key_findings,
        report_type=req.report_type
    )
    return result

