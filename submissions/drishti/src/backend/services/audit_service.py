"""
DRISHTI — Agent Audit & Transparency Service
Logs all agent actions, tool calls, SQL queries, and reasoning steps into Db2.
"""
import time
import logging
from typing import Optional, List, Dict, Any
from backend.core.db2 import execute_statement, fetch_all

logger = logging.getLogger("drishti.audit")

def log_agent_action(
    session_id: str,
    agent_name: str,
    action_type: str,
    status: str = "SUCCESS",
    sql_query: Optional[str] = None,
    execution_time_ms: Optional[int] = None,
    reasoning_summary: Optional[str] = None,
) -> None:
    """Safely log an agent action to AGENT_AUDIT_LOGS table in Db2."""
    sql = """
        INSERT INTO AGENT_AUDIT_LOGS (
            session_id, agent_name, action_type, sql_query, execution_time_ms, status, reasoning_summary
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    try:
        execute_statement(
            sql,
            (
                session_id,
                agent_name,
                action_type,
                sql_query[:2048] if sql_query else None,
                execution_time_ms,
                status,
                reasoning_summary[:1024] if reasoning_summary else None,
            )
        )
    except Exception as e:
        logger.error(f"Failed to write agent audit log: {e}")

def get_session_audit_logs(session_id: str) -> List[Dict[str, Any]]:
    """Retrieve all audit logs for a specific workflow session."""
    sql = """
        SELECT log_id, session_id, agent_name, action_type, sql_query,
               execution_time_ms, status, reasoning_summary, created_at
        FROM AGENT_AUDIT_LOGS
        WHERE session_id = ?
        ORDER BY created_at ASC
    """
    return fetch_all(sql, (session_id,))

def get_recent_audit_logs(limit: int = 50) -> List[Dict[str, Any]]:
    """Retrieve latest audit activity across all agents."""
    sql = f"""
        SELECT log_id, session_id, agent_name, action_type, sql_query,
               execution_time_ms, status, reasoning_summary, created_at
        FROM AGENT_AUDIT_LOGS
        ORDER BY created_at DESC
        FETCH FIRST {int(limit)} ROWS ONLY
    """
    return fetch_all(sql)

