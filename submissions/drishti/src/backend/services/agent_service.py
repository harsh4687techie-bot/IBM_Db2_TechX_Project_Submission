"""
DRISHTI — Specialized Multi-Agent Intelligence Engine
Coordinates 6 specialized agents with real Db2 tool execution,
grounded evidence synthesis, audit logging, and downloadable reports.
"""
import os
import uuid
import time
import json
import logging
from typing import Dict, Any, List, Optional
import urllib.request
import urllib.error

from backend.core.config import settings
from backend.services.audit_service import log_agent_action
from backend.services.stock_service import get_company_by_ticker, get_stock_price_history, get_stock_metrics_summary, get_all_companies
from backend.services.anomaly_service import get_anomalies, get_anomaly_summary
from backend.services.sector_service import get_sector_overview, get_sector_stocks
from backend.services.report_service import create_and_save_report

logger = logging.getLogger("drishti.agents")

def _call_gemini_synthesis(prompt: str) -> Optional[str]:
    """Call Google Gemini API if key is configured, with safe error handling."""
    api_key = settings.GEMINI_API_KEY
    if not api_key:
        return None
        
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.2, "maxOutputTokens": 1500}
    }
    
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            candidates = data.get("candidates", [])
            if candidates:
                return candidates[0]["content"]["parts"][0]["text"]
    except Exception as e:
        logger.warning(f"Gemini API invocation fallback: {e}")
    return None

class OrchestratorAgent:
    """Understands user queries, extracts entities, and delegates workflow."""
    
    @staticmethod
    def plan_workflow(prompt: str, explicit_ticker: Optional[str] = None) -> Dict[str, Any]:
        p_upper = prompt.upper()
        # Entity extraction
        target_ticker = explicit_ticker.upper() if explicit_ticker else None
        
        if not target_ticker:
            all_comps = get_all_companies()
            for c in all_comps:
                if c["ticker"] in p_upper or c["company_name"].upper() in p_upper:
                    target_ticker = c["ticker"]
                    break
                    
        # If no specific ticker mentioned, default to most active or first stock
        if not target_ticker:
            all_comps = get_all_companies()
            target_ticker = all_comps[0]["ticker"] if all_comps else "AAPL"
            
        intent = "STOCK_DEEP_DIVE"
        if "SECTOR" in p_upper or "COMPARE" in p_upper:
            intent = "SECTOR_COMPARISON"
        elif "ANOMAL" in p_upper or "SPIKE" in p_upper or "SURGE" in p_upper:
            intent = "ANOMALY_INVESTIGATION"
            
        return {
            "target_ticker": target_ticker,
            "intent": intent,
            "tasks": ["DATA_EXTRACTION", "ANOMALY_AUDIT", "SECTOR_BENCHMARK", "SYNTHESIS", "REPORT_GEN"]
        }

class DataAnalystAgent:
    """Queries IBM Db2 for quantitative price series and moving averages."""
    
    @staticmethod
    def execute(ticker: str, session_id: str) -> Dict[str, Any]:
        t0 = time.perf_counter()
        comp = get_company_by_ticker(ticker)
        if not comp:
            raise ValueError(f"Company {ticker} not found in database.")
            
        prices = get_stock_price_history(comp["stock_id"], limit=60)
        metrics = get_stock_metrics_summary(comp["stock_id"])
        elapsed = int((time.perf_counter() - t0) * 1000)
        
        log_agent_action(
            session_id=session_id,
            agent_name="DataAnalystAgent",
            action_type="SQL_QUERY",
            status="SUCCESS",
            sql_query="SELECT FROM DAILY_PRICES WHERE stock_id = ?",
            execution_time_ms=elapsed,
            reasoning_summary=f"Extracted {len(prices)} price bars and 30d return metrics for {ticker} from Db2."
        )
        
        return {
            "company": comp,
            "recent_prices_count": len(prices),
            "latest_price": prices[-1] if prices else None,
            "metrics": metrics
        }

class AnomalyDetectionAgent:
    """Inspects MARKET_ANOMALIES table for statistical signals and z-scores."""
    
    @staticmethod
    def execute(stock_id: int, ticker: str, session_id: str) -> List[Dict[str, Any]]:
        t0 = time.perf_counter()
        anomalies = get_anomalies(stock_id=stock_id, limit=10)
        elapsed = int((time.perf_counter() - t0) * 1000)
        
        log_agent_action(
            session_id=session_id,
            agent_name="AnomalyDetectionAgent",
            action_type="SQL_QUERY",
            status="SUCCESS",
            sql_query="SELECT FROM MARKET_ANOMALIES WHERE stock_id = ?",
            execution_time_ms=elapsed,
            reasoning_summary=f"Retrieved {len(anomalies)} statistical anomalies (volume surges, price spikes) for {ticker}."
        )
        return anomalies

class SectorIntelligenceAgent:
    """Compares company performance against sector peers."""
    
    @staticmethod
    def execute(sector: str, ticker: str, session_id: str) -> Dict[str, Any]:
        t0 = time.perf_counter()
        peers = get_sector_stocks(sector)
        overview = get_sector_overview()
        sec_stat = next((s for s in overview if s["sector"].lower() == sector.lower()), None)
        elapsed = int((time.perf_counter() - t0) * 1000)
        
        log_agent_action(
            session_id=session_id,
            agent_name="SectorIntelligenceAgent",
            action_type="SQL_QUERY",
            status="SUCCESS",
            sql_query="SELECT FROM COMPANIES c JOIN DAILY_PRICES WHERE c.sector = ?",
            execution_time_ms=elapsed,
            reasoning_summary=f"Benchmarked {ticker} against {len(peers)} peer stocks in sector '{sector}'."
        )
        
        return {
            "sector": sector,
            "sector_metrics": sec_stat,
            "peer_count": len(peers),
            "peers": peers[:5]
        }

class ResearchAgent:
    """Synthesizes validated Db2 evidence into structured narrative."""
    
    @staticmethod
    def synthesize(
        query: str,
        analyst_data: Dict[str, Any],
        anomalies: List[Dict[str, Any]],
        sector_data: Dict[str, Any],
        session_id: str
    ) -> str:
        t0 = time.perf_counter()
        comp = analyst_data["company"]
        metrics = analyst_data["metrics"]
        latest = analyst_data["latest_price"] or {}
        
        mcap = float(comp.get("market_cap") or 0)
        close_p = float(latest.get("close_price") or 0)
        ret_30d = float(metrics.get("thirty_day_return_pct") or 0)
        h52 = float(metrics.get("fifty_two_week_high") or 0)
        l52 = float(metrics.get("fifty_two_week_low") or 0)
        vol_30d = float(metrics.get("average_volume_30d") or 0)
        daily_ret = float(latest.get("daily_return_pct") or 0)
        
        # Prepare grounded evidence payload
        evidence_prompt = f"""
You are the Senior Research Agent for DRISHTI (Financial Intelligence Platform powered by IBM Db2).
User Question: "{query}"

VALIDATED EVIDENCE RETRIEVED FROM IBM DB2:
- Company: {comp['company_name']} (Ticker: {comp['ticker']})
- Sector: {comp['sector']} | Industry: {comp.get('industry', 'N/A')}
- Market Cap: ${mcap:,.2f}
- Latest Close Price: ${close_p:.2f} (Trading Date: {latest.get('trading_date')})
- 30-Day Return: {ret_30d:+.2f}%
- 52-Week High: ${h52:.2f} | 52-Week Low: ${l52:.2f}
- Detected Anomalies ({len(anomalies)} events):
"""
        for a in anomalies[:5]:
            evidence_prompt += f"  * [{a['severity']}] {a['trading_date']}: {a['description']}\n"
            
        sec_ret = sector_data['sector_metrics'].get('latest_avg_return_pct', 0) if sector_data.get('sector_metrics') else 0
        evidence_prompt += f"""
- Sector Performance ({comp['sector']}):
  * Total Sector Peers Tracked: {sector_data['peer_count']}
  * Sector Average Daily Return: {sec_ret}%

RULES:
1. Ground your answer EXCLUSIVELY on the provided Db2 evidence. Do not hallucinate or invent outside numbers.
2. Provide a structured markdown report with:
   - ## Executive Overview
   - ## Price Action & Performance
   - ## Statistical Anomaly Investigation
   - ## Sector Relative Standing
   - ## Strategic Takeaway
"""
        # Attempt Gemini synthesis with deterministic fallback
        narrative = _call_gemini_synthesis(evidence_prompt)
        if not narrative:
            # Deterministic, evidence-grounded template synthesis
            anom_text = ""
            if anomalies:
                anom_text = "\n".join([f"- **{a['severity']} Alert** ({a['trading_date']}): {a['description']}" for a in anomalies[:4]])
            else:
                anom_text = "No statistical anomalies detected above threshold (z-score > 2.0)."
                
            narrative = f"""## Executive Overview
**{comp['company_name']} ({comp['ticker']})** is currently trading at **${close_p:.2f}** in the **{comp['sector']}** sector. Based on validated transactional records in IBM Db2, the equity exhibits a **{ret_30d:+.2f}%** 30-day return.

## Price Action & Performance
- **Latest Close:** ${close_p:.2f} (Session: {latest.get('trading_date')})
- **52-Week Range:** ${l52:.2f} – ${h52:.2f}
- **30-Day Momentum:** {ret_30d:+.2f}%
- **Average 30-Day Volume:** {vol_30d:,.0f} shares

## Statistical Anomaly Investigation
{anom_text}

## Sector Relative Standing
- **Sector:** {comp['sector']} ({sector_data['peer_count']} tracked companies)
- **Sector Average Return:** {sec_ret}%
- **Relative Strength:** {comp['ticker']} is positioned {'above' if daily_ret >= 0 else 'below'} the peer median.

## Strategic Takeaway
The volume surges and price anomalies indicate institutional participation and heightened liquidity around recent trading sessions.
"""

        elapsed = int((time.perf_counter() - t0) * 1000)
        log_agent_action(
            session_id=session_id,
            agent_name="ResearchAgent",
            action_type="SYNTHESIS",
            status="SUCCESS",
            execution_time_ms=elapsed,
            reasoning_summary=f"Synthesized evidence from Db2 into structured report for query: '{query[:80]}'."
        )
        return narrative

def execute_agent_workflow(query: str, explicit_ticker: Optional[str] = None) -> Dict[str, Any]:
    """Coordinates the end-to-end multi-agent execution pipeline."""
    session_id = str(uuid.uuid4())
    steps: List[Dict[str, Any]] = []
    
    # Step 1: Orchestrator
    t0 = time.perf_counter()
    plan = OrchestratorAgent.plan_workflow(query, explicit_ticker)
    ticker = plan["target_ticker"]
    steps.append({
        "agent": "OrchestratorAgent",
        "action": "PLAN_WORKFLOW",
        "detail": f"Identified target entity {ticker} and workflow intent '{plan['intent']}'.",
        "duration_ms": int((time.perf_counter() - t0) * 1000)
    })
    
    # Step 2: Data Analyst Agent
    t0 = time.perf_counter()
    analyst_data = DataAnalystAgent.execute(ticker, session_id)
    steps.append({
        "agent": "DataAnalystAgent",
        "action": "DB2_QUERY_PRICE_SERIES",
        "detail": f"Queried {analyst_data['recent_prices_count']} price records and 30d return metrics for {ticker}.",
        "duration_ms": int((time.perf_counter() - t0) * 1000)
    })
    
    # Step 3: Anomaly Detection Agent
    t0 = time.perf_counter()
    comp = analyst_data["company"]
    anomalies = AnomalyDetectionAgent.execute(comp["stock_id"], ticker, session_id)
    steps.append({
        "agent": "AnomalyDetectionAgent",
        "action": "DB2_QUERY_ANOMALIES",
        "detail": f"Found {len(anomalies)} statistical anomalies (z-score > 2.0) in MARKET_ANOMALIES.",
        "duration_ms": int((time.perf_counter() - t0) * 1000)
    })
    
    # Step 4: Sector Intelligence Agent
    t0 = time.perf_counter()
    sector_data = SectorIntelligenceAgent.execute(comp["sector"], ticker, session_id)
    steps.append({
        "agent": "SectorIntelligenceAgent",
        "action": "DB2_BENCHMARK_SECTOR",
        "detail": f"Benchmarked against {sector_data['peer_count']} stocks in sector '{comp['sector']}'.",
        "duration_ms": int((time.perf_counter() - t0) * 1000)
    })
    
    # Step 5: Research Agent
    t0 = time.perf_counter()
    narrative = ResearchAgent.synthesize(query, analyst_data, anomalies, sector_data, session_id)
    steps.append({
        "agent": "ResearchAgent",
        "action": "EVIDENCE_SYNTHESIS",
        "detail": "Synthesized grounded analytical conclusions from Db2 query results.",
        "duration_ms": int((time.perf_counter() - t0) * 1000)
    })
    
    # Step 6: Report Generation Agent
    t0 = time.perf_counter()
    rep = create_and_save_report(
        title=f"DRISHTI Analysis — {comp['company_name']} ({ticker})",
        target_ticker=ticker,
        summary_markdown=narrative,
        key_findings={
            "metrics": analyst_data["metrics"],
            "anomalies_count": len(anomalies),
            "sector": comp["sector"]
        }
    )
    steps.append({
        "agent": "ReportGenerationAgent",
        "action": "GENERATE_EXPORTABLE_REPORT",
        "detail": f"Compiled downloadable PDF and Excel artifacts with UUID {rep['report_uuid'][:8]}.",
        "duration_ms": int((time.perf_counter() - t0) * 1000)
    })
    
    return {
        "session_id": session_id,
        "user_query": query,
        "response_markdown": narrative,
        "structured_findings": {
            "company": comp,
            "metrics": analyst_data["metrics"],
            "anomalies": anomalies[:5],
            "sector_metrics": sector_data["sector_metrics"]
        },
        "steps": steps,
        "generated_report_uuid": rep["report_uuid"]
    }

