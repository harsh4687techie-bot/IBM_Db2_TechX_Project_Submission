"""
DRISHTI — Health & Diagnostics Router
"""
from fastapi import APIRouter
from backend.core.db2 import ping_db
from backend.core.config import settings

router = APIRouter(prefix="/api/health", tags=["Health"])

@router.get("")
def get_system_health():
    """Returns application status and IBM Db2 live connection health."""
    db_health = ping_db()
    return {
        "status": "online",
        "platform": settings.PROJECT_NAME,
        "tagline": settings.TAGLINE,
        "version": settings.VERSION,
        "database": db_health
    }

