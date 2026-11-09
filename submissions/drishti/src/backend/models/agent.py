"""
DRISHTI — Agent Execution & Audit Models
"""
from typing import Optional, List, Any
from datetime import datetime
from pydantic import BaseModel, Field

class AgentActionLog(BaseModel):
    log_id: int
    session_id: str
    agent_name: str
    action_type: str
    sql_query: Optional[str] = None
    execution_time_ms: Optional[int] = None
    status: str
    reasoning_summary: Optional[str] = None
    created_at: Optional[datetime] = None

class AgentQueryRequest(BaseModel):
    prompt: str = Field(..., description="Natural language question or analysis request")
    session_id: Optional[str] = None
    target_ticker: Optional[str] = None

class AgentStepTrace(BaseModel):
    agent: str
    action: str
    detail: str
    sql_query: Optional[str] = None
    duration_ms: Optional[int] = None

class AgentQueryResponse(BaseModel):
    session_id: str
    user_query: str
    response_markdown: str
    structured_findings: Optional[dict[str, Any]] = None
    steps: List[AgentStepTrace] = []
    generated_report_uuid: Optional[str] = None

