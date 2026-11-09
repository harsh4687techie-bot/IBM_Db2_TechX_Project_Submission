"""
DRISHTI — Agentic Data Intelligence Platform
FastAPI Application Entry Point
"""
import sys
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.core.config import settings
from backend.core.db2 import ping_db
from backend.routers import health, stocks, anomalies, sectors, ingestion, reports, agents

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup validation
    print(f"\n{'=' * 60}")
    print(f"  {settings.PROJECT_NAME} — {settings.TAGLINE}")
    print(f"  Backend API Initializing on http://{settings.BACKEND_HOST}:{settings.BACKEND_PORT}")
    print(f"{'=' * 60}")
    try:
        health_info = ping_db()
        print(f"[+] IBM Db2 Connection: HEALTHY (Latency: {health_info['latency_ms']}ms)")
        print(f"[+] Connected to Database: {health_info['database']} ({health_info['dbms_name']} v{health_info['dbms_version']})")
    except Exception as e:
        print(f"[-] IBM Db2 Startup Ping Failed: {e}")
    yield
    print("[*] DRISHTI Backend shutting down.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=f"Agentic Data Intelligence Platform using IBM Db2 as core database. Tagline: {settings.TAGLINE}",
    version=settings.VERSION,
    lifespan=lifespan
)

# CORS Middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(health.router)
app.include_router(stocks.router)
app.include_router(anomalies.router)
app.include_router(sectors.router)
app.include_router(ingestion.router)
app.include_router(reports.router)
app.include_router(agents.router)

# Mount Frontend static distribution if present
dist_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend", "dist")
if os.path.isdir(dist_dir):
    app.mount("/app", StaticFiles(directory=dist_dir, html=True), name="frontend")

@app.get("/")
def root():
    return {
        "platform": settings.PROJECT_NAME,
        "tagline": settings.TAGLINE,
        "status": "online",
        "frontend_app": "/app/",
        "docs_url": "/docs",
        "api_endpoints": [
            "/api/health",
            "/api/stocks",
            "/api/anomalies",
            "/api/sectors",
            "/api/ingestion/seed-sample",
            "/api/reports",
            "/api/agents/chat"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host=settings.BACKEND_HOST,
        port=settings.BACKEND_PORT,
        reload=True
    )

