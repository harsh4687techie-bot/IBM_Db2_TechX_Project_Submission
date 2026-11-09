"""
DRISHTI — Application Configuration Settings
Loads environment variables safely with defaults.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Base project directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_PATH = BASE_DIR / ".env"

load_dotenv(dotenv_path=ENV_PATH)

class Settings:
    PROJECT_NAME: str = "DRISHTI"
    TAGLINE: str = "See Beyond Data."
    VERSION: str = "1.0.0"
    
    # IBM Db2 Configuration
    DB2_HOST: str = os.getenv("DB2_HOST", "127.0.0.1")
    DB2_PORT: str = os.getenv("DB2_PORT", "50000")
    DB2_DATABASE: str = os.getenv("DB2_DATABASE", "DRISHTI")
    DB2_USER: str = os.getenv("DB2_USER", "db2inst1")
    DB2_PASSWORD: str = os.getenv("DB2_PASSWORD", "")
    
    # AI Model Provider
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # Server & Security
    BACKEND_HOST: str = os.getenv("BACKEND_HOST", "127.0.0.1")
    BACKEND_PORT: int = int(os.getenv("BACKEND_PORT", "8000"))
    CORS_ORIGINS: list[str] = [
        origin.strip()
        for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")
        if origin.strip()
    ]
    APP_ENV: str = os.getenv("APP_ENV", "development")
    
    # File storage
    EXPORTS_DIR: Path = BASE_DIR / "backend" / "exports"

settings = Settings()

