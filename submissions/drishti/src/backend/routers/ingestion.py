"""
DRISHTI — Data Ingestion API Router
Handles file uploads (CSV, Excel) and sample market data seeding into IBM Db2.
"""
import io
import pandas as pd
from fastapi import APIRouter, UploadFile, File, HTTPException
from backend.services.ingestion_service import (
    validate_and_ingest_dataframe,
    seed_sample_market_data
)

router = APIRouter(prefix="/api/ingestion", tags=["Data Ingestion"])

@router.post("/seed-sample")
def seed_market_data():
    """
    Seeds DRISHTI with 6 realistic market leaders (AAPL, NVDA, MSFT, JPM, JNJ, XOM)
    spanning Technology, Financials, Healthcare, and Energy with 90 trading days.
    """
    result = seed_sample_market_data()
    return result

@router.post("/upload")
async def upload_dataset(file: UploadFile = File(...)):
    """Uploads and validates a CSV or Excel market data file."""
    filename = file.filename or ""
    lower_name = filename.lower()
    
    if not (lower_name.endswith(".csv") or lower_name.endswith(".xlsx") or lower_name.endswith(".xls")):
        raise HTTPException(status_code=400, detail="Invalid file type. Only .csv, .xlsx, and .xls files are supported.")
        
    content = await file.read()
    if len(content) > 25 * 1024 * 1024:  # 25 MB limit
        raise HTTPException(status_code=400, detail="File size exceeds maximum allowable limit of 25MB.")
        
    try:
        if lower_name.endswith(".csv"):
            df = pd.read_csv(io.BytesIO(content))
        else:
            df = pd.read_excel(io.BytesIO(content))
            
        result = validate_and_ingest_dataframe(df)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Data ingestion failed: {str(e)}")

