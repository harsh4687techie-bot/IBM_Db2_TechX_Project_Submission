"""
DRISHTI — IBM Db2 Connection & Query Execution Manager
Provides thread-safe connections, parameterized query execution,
transaction management, and error masking.
"""
import os
import sys
import time
import logging
import threading
from contextlib import contextmanager
from typing import Any, Dict, List, Optional, Tuple

from backend.core.config import settings

logger = logging.getLogger("drishti.db2")
_db_lock = threading.RLock()

# Ensure clidriver DLL paths are registered on Windows before importing ibm_db
if sys.platform == "win32":
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
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

import ibm_db

def _mask_secret(msg: str) -> str:
    """Mask password or credentials from error messages."""
    if settings.DB2_PASSWORD and settings.DB2_PASSWORD in msg:
        return msg.replace(settings.DB2_PASSWORD, "[MASKED]")
    return msg

def get_connection_string() -> str:
    """Build the connection string securely."""
    return (
        f"DATABASE={settings.DB2_DATABASE};"
        f"HOSTNAME={settings.DB2_HOST};"
        f"PORT={settings.DB2_PORT};"
        f"PROTOCOL=TCPIP;"
        f"UID={settings.DB2_USER};"
        f"PWD={settings.DB2_PASSWORD};"
    )

@contextmanager
def get_db_connection():
    """Context manager for acquiring and closing a Db2 connection safely with thread synchronization."""
    with _db_lock:
        conn_str = get_connection_string()
        conn = None
        try:
            conn = ibm_db.connect(conn_str, "", "")
            yield conn
        except Exception as e:
            safe_err = _mask_secret(str(e))
            logger.error(f"Db2 Connection Exception: {safe_err}")
            raise RuntimeError(f"Database error: {safe_err}") from None
        finally:
            if conn:
                try:
                    ibm_db.close(conn)
                except Exception:
                    pass

def ping_db() -> Dict[str, Any]:
    """Test connection to Db2 and return server metadata and latency."""
    t0 = time.perf_counter()
    with get_db_connection() as conn:
        server_info = ibm_db.server_info(conn)
        sql = "SELECT CURRENT TIMESTAMP AS NOW, CURRENT SERVER AS SERVER FROM SYSIBM.SYSDUMMY1"
        stmt = ibm_db.exec_immediate(conn, sql)
        row = ibm_db.fetch_assoc(stmt)
        elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)
        
        return {
            "status": "healthy",
            "latency_ms": elapsed_ms,
            "database": getattr(server_info, "DB_NAME", settings.DB2_DATABASE),
            "dbms_name": getattr(server_info, "DBMS_NAME", "DB2"),
            "dbms_version": getattr(server_info, "DBMS_VER", "Unknown"),
            "server_timestamp": str(row.get("NOW", "")),
        }

def fetch_all(sql: str, params: Tuple[Any, ...] = ()) -> List[Dict[str, Any]]:
    """Execute a parameterized SELECT statement and return all rows as dicts."""
    with get_db_connection() as conn:
        try:
            stmt = ibm_db.prepare(conn, sql)
            if not stmt:
                err_msg = ibm_db.stmt_errormsg() or "Failed to prepare SQL statement"
                raise RuntimeError(err_msg)
            for idx, val in enumerate(params, start=1):
                ibm_db.bind_param(stmt, idx, val)
            ibm_db.execute(stmt)
            
            rows = []
            row = ibm_db.fetch_assoc(stmt)
            while row:
                # Normalize keys to lowercase for cleaner JSON response
                rows.append({k.lower(): v for k, v in row.items()})
                row = ibm_db.fetch_assoc(stmt)
            return rows
        except Exception as e:
            safe_err = _mask_secret(str(e))
            logger.error(f"SQL execution error on '{sql}': {safe_err}")
            raise RuntimeError(f"Query execution failed: {safe_err}") from None

def fetch_one(sql: str, params: Tuple[Any, ...] = ()) -> Optional[Dict[str, Any]]:
    """Execute a parameterized SELECT statement and return a single row or None."""
    rows = fetch_all(sql, params)
    return rows[0] if rows else None

def execute_statement(sql: str, params: Tuple[Any, ...] = ()) -> int:
    """Execute an INSERT, UPDATE, or DELETE statement and return rows affected."""
    with get_db_connection() as conn:
        try:
            stmt = ibm_db.prepare(conn, sql)
            if not stmt:
                err_msg = ibm_db.stmt_errormsg() or "Failed to prepare SQL statement"
                raise RuntimeError(err_msg)
            for idx, val in enumerate(params, start=1):
                ibm_db.bind_param(stmt, idx, val)
            ibm_db.execute(stmt)
            return ibm_db.num_rows(stmt)
        except Exception as e:
            safe_err = _mask_secret(str(e))
            logger.error(f"SQL execute statement error on '{sql}': {safe_err}")
            raise RuntimeError(f"Statement execution failed: {safe_err}") from None

