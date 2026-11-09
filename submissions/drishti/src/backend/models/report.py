"""
DRISHTI — Analysis Report Models
"""
from typing import Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field

class ReportCreateRequest(BaseModel):
    report_title: str
    target_ticker: Optional[str] = None
    report_type: str = Field("STOCK_DEEP_DIVE", description="STOCK_DEEP_DIVE, SECTOR_OVERVIEW, ANOMALY_DIGEST")
    summary_markdown: str
    key_findings: Optional[dict[str, Any]] = None

class ReportItem(BaseModel):
    report_id: int
    report_uuid: str
    report_title: str
    target_ticker: Optional[str] = None
    report_type: str
    summary_markdown: Optional[str] = None
    key_findings_json: Optional[str] = None
    file_path_pdf: Optional[str] = None
    file_path_excel: Optional[str] = None
    generated_by: str
    created_at: Optional[datetime] = None

