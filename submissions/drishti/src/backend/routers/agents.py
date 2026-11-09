"""
DRISHTI — Specialized AI Agents Router
Dispatches natural language prompts to multi-agent intelligence pipeline and exposes audit logs.
"""
from fastapi import APIRouter, HTTPException
from backend.models.agent import AgentQueryRequest, AgentQueryResponse
from backend.services.agent_service import execute_agent_workflow
from backend.services.audit_service import get_session_audit_logs, get_recent_audit_logs

router = APIRouter(prefix="/api/agents", tags=["Agentic AI"])

@router.post("/chat", response_model=AgentQueryResponse)
def execute_agent_chat(req: AgentQueryRequest):
    """
    Submits a natural language market inquiry to the 6 specialized AI agents.
    Executes live SQL queries on Db2 and returns evidence-backed report and audit traces.
    """
    if not req.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt query cannot be empty.")
        
    try:
        response = execute_agent_workflow(
            query=req.prompt,
            explicit_ticker=req.target_ticker
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent workflow execution failed: {str(e)}")

@router.get("/audit/{session_id}")
def get_audit_trail_for_session(session_id: str):
    """Retrieve full audit log trail for an agent session."""
    return get_session_audit_logs(session_id)

@router.get("/audit")
def list_recent_audit_logs(limit: int = 50):
    """Retrieve the latest agent actions and SQL executions across all sessions."""
    return get_recent_audit_logs(limit=limit)

