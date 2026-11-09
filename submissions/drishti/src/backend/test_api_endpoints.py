"""
DRISHTI — Backend Service & Router Integration Test Suite
Tests health, ingestion, stock queries, anomaly detection, sector metrics,
multi-agent workflows, and report generation directly against Db2.
"""
import sys
import os
import json

# Ensure base directory is in sys.path
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

# Ensure clidriver DLL paths are registered on Windows
if sys.platform == "win32":
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

from backend.routers import health, stocks, anomalies, sectors, ingestion, reports, agents
from backend.models.agent import AgentQueryRequest

def run_tests():
    print("=" * 65)
    print("  DRISHTI — Backend API & Multi-Agent Integration Tests")
    print("=" * 65)
    
    # Test 1: Health check
    print("\n[TEST 1] Testing Health Diagnostics...")
    health_res = health.get_system_health()
    print(f"  Health Status:   {health_res['status']}")
    print(f"  Db2 Latency:     {health_res['database']['latency_ms']} ms")
    print(f"  Db2 Engine:      {health_res['database']['dbms_name']} v{health_res['database']['dbms_version']}")
    assert health_res["status"] == "online"
    assert health_res["database"]["status"] == "healthy"
    
    # Test 2: Ingest sample data
    print("\n[TEST 2] Testing Market Data Ingestion & Seeding...")
    seed_res = ingestion.seed_market_data()
    print(f"  Companies Created:   {seed_res.get('new_companies_created')}")
    print(f"  Prices Inserted:     {seed_res.get('prices_inserted')}")
    print(f"  Anomalies Detected:  {seed_res.get('anomalies_detected')}")
    assert seed_res["status"] == "success"
    
    # Test 3: List stocks
    print("\n[TEST 3] Testing Stock Query Services...")
    all_stocks = stocks.list_stocks()
    print(f"  Tracked Companies ({len(all_stocks)} total):")
    for s in all_stocks:
        print(f"    * {s['ticker']:<6} | {s['company_name']:<24} | Sector: {s['sector']:<12} | Latest: ${float(s['latest_close'] or 0):.2f}")
    assert len(all_stocks) >= 6
    
    # Test 4: Stock detail & prices
    print("\n[TEST 4] Testing Stock Details for NVDA...")
    detail = stocks.get_stock_detail("NVDA")
    print(f"  NVDA 30d Return:  {detail['metrics']['thirty_day_return_pct']:+.2f}%")
    print(f"  NVDA 52w High:    ${float(detail['metrics']['fifty_two_week_high'] or 0):.2f}")
    prices = stocks.get_stock_prices("NVDA", limit=10)
    print(f"  Retrieved {len(prices)} price bars for NVDA.")
    assert len(prices) > 0
    
    # Test 5: Anomaly Summary & List
    print("\n[TEST 5] Testing Statistical Anomaly Detection Results...")
    anom_summary = anomalies.get_summary()
    print(f"  Total Anomalies in Db2: {anom_summary['total_anomalies']}")
    print(f"  Critical Count:         {anom_summary['critical_count']}")
    print(f"  High Count:             {anom_summary['high_count']}")
    print(f"  By Type Breakdown:      {anom_summary['by_type']}")
    recent_anoms = anomalies.list_anomalies(limit=3)
    for a in recent_anoms:
        print(f"    * [{a['severity']:<8}] {a['ticker']}: {a['description'][:65]}...")
    assert anom_summary["total_anomalies"] > 0
    
    # Test 6: Sector Intelligence
    print("\n[TEST 6] Testing Sector Intelligence & Rollups...")
    sec_overview = sectors.list_sectors()
    print(f"  Sector Rollups ({len(sec_overview)} sectors):")
    for sec in sec_overview:
        print(f"    * {sec['sector']:<14} | Stocks: {sec['stock_count']} | Latest Return: {sec['latest_avg_return_pct']:+.2f}% | Anomalies: {sec['anomaly_count']}")
    assert len(sec_overview) >= 4
    
    # Test 7: Multi-Agent Workflow Execution
    print("\n[TEST 7] Testing 6-Agent Collaboration Pipeline (/api/agents/chat)...")
    chat_req = AgentQueryRequest(
        prompt="Analyze NVIDIA's recent volume surges and compare performance against technology sector peers.",
        target_ticker="NVDA"
    )
    agent_res = agents.execute_agent_chat(chat_req)
    print(f"  Session ID:            {agent_res['session_id']}")
    print(f"  Generated Report UUID: {agent_res['generated_report_uuid']}")
    print(f"  Agent Execution Steps ({len(agent_res['steps'])} steps executed):")
    for st in agent_res['steps']:
        print(f"    -> [{st['agent']:<24}] {st['action']:<25} ({st['duration_ms']}ms)")
        
    print("\n  Executive Narrative Preview:")
    for line in agent_res['response_markdown'].split("\n")[:8]:
        print(f"    {line}")
        
    assert len(agent_res['steps']) == 6
    assert agent_res['generated_report_uuid'] is not None
    
    # Test 8: Reports Persistence & Retrieval
    print("\n[TEST 8] Testing Report Retrieval & File Artifacts...")
    all_reports = reports.list_reports()
    print(f"  Persisted Reports in Db2: {len(all_reports)}")
    latest_rep = reports.get_report(agent_res['generated_report_uuid'])
    print(f"  Report Title: {latest_rep['report_title']}")
    print(f"  PDF Artifact on disk:   {os.path.exists(latest_rep['file_path_pdf'])}")
    print(f"  Excel Artifact on disk: {os.path.exists(latest_rep['file_path_excel'])}")
    assert os.path.exists(latest_rep["file_path_pdf"])
    assert os.path.exists(latest_rep["file_path_excel"])
    
    # Test 9: Agent Audit Logging
    print("\n[TEST 9] Testing Agent Audit Trail in Db2...")
    audit_logs = agents.list_recent_audit_logs(limit=6)
    print(f"  Audit Logs Recorded in Db2 ({len(audit_logs)} latest actions):")
    for log in audit_logs[:4]:
        print(f"    * [{log['agent_name']:<24}] {log['action_type']:<12} | Status: {log['status']} | {log['reasoning_summary'][:55]}...")
    assert len(audit_logs) >= 4
    
    print("\n" + "=" * 65)
    print("  ALL 9 INTEGRATION TESTS PASSED WITH ZERO ERRORS!")
    print("=" * 65)

if __name__ == "__main__":
    run_tests()
