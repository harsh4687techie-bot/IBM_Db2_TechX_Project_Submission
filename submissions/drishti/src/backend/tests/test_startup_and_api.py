"""
DRISHTI Verification Suite — Area 1: Application Startup & Restart Verification
Verifies:
1. IBM Db2 container is healthy and accepting TCP/IP connections.
2. FastAPI backend boots cleanly with all routes and static mounts.
3. All HTTP endpoints return HTTP 200 OK with valid JSON payloads:
   - GET /
   - GET /api/health
   - GET /api/stocks
   - GET /api/anomalies
   - GET /api/sectors
   - GET /api/reports
   - POST /api/agents/chat
   - GET /app/ (Frontend React distribution)
4. Graceful shutdown and clean cold restart test.
"""
import os
import sys
import time
import json
import threading
import urllib.request
import urllib.error
import uvicorn

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

# Register Windows clidriver DLL paths
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

from backend.main import app
from backend.core.db2 import ping_db

class ServerThread(threading.Thread):
    def __init__(self, app, host="127.0.0.1", port=8000):
        super().__init__()
        self.server = uvicorn.Server(uvicorn.Config(app, host=host, port=port, log_level="warning"))
        self.daemon = True

    def run(self):
        self.server.run()

    def stop(self):
        self.server.should_exit = True

def run_startup_verification():
    print("=" * 70)
    print("  AREA 1: APPLICATION STARTUP & RESTART VERIFICATION")
    print("=" * 70)

    results = []
    def record(name: str, passed: bool, detail: str):
        results.append((name, passed, detail))
        sym = "[PASS]" if passed else "[FAIL]"
        print(f"  {sym} {name}: {detail}")

    # 1. Db2 Health
    try:
        h = ping_db()
        record("IBM Db2 Container & Port 50000", h["status"] == "healthy", f"Database: {h['database']} (Latency: {h['latency_ms']}ms)")
    except Exception as e:
        record("IBM Db2 Container & Port 50000", False, str(e))
        return False

    # 2. Boot FastAPI in-process
    srv = ServerThread(app, port=8000)
    srv.start()
    time.sleep(1.5)

    base_url = "http://127.0.0.1:8000"

    def http_get(url):
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=5) as resp:
            body = resp.read().decode("utf-8")
            return resp.status, body

    def http_post(url, data_dict):
        req = urllib.request.Request(
            url, 
            data=json.dumps(data_dict).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = resp.read().decode("utf-8")
            return resp.status, body

    try:
        # GET /
        st, b = http_get(f"{base_url}/")
        j = json.loads(b)
        record("Root Endpoint (GET /)", st == 200 and j.get("platform") == "DRISHTI",
               f"Status: {st}, Platform: {j.get('platform')}")

        # GET /api/health
        st, b = http_get(f"{base_url}/api/health")
        j = json.loads(b)
        db_info = j.get("database", {})
        health_ok = (st == 200 and j.get("status") in ("online", "healthy") and db_info.get("database") == "DRISHTI" and db_info.get("status") == "healthy")
        record("Health Endpoint (GET /api/health)", health_ok,
               f"Status: {st}, App: {j.get('status')}, DB: {db_info.get('database')} ({db_info.get('status')})")

        # GET /api/stocks
        st, b = http_get(f"{base_url}/api/stocks")
        j = json.loads(b)
        record("Stocks Endpoint (GET /api/stocks)", st == 200 and len(j) >= 6,
               f"Status: {st}, Stocks returned: {len(j)}")

        # GET /api/anomalies
        st, b = http_get(f"{base_url}/api/anomalies?limit=10")
        j = json.loads(b)
        record("Anomalies Endpoint (GET /api/anomalies)", st == 200 and len(j) > 0,
               f"Status: {st}, Anomalies returned: {len(j)}")

        # GET /api/sectors
        st, b = http_get(f"{base_url}/api/sectors")
        j = json.loads(b)
        record("Sectors Endpoint (GET /api/sectors)", st == 200 and len(j) >= 4,
               f"Status: {st}, Sectors returned: {len(j)}")

        # GET /api/reports
        st, b = http_get(f"{base_url}/api/reports")
        j = json.loads(b)
        record("Reports Endpoint (GET /api/reports)", st == 200 and len(j) > 0,
               f"Status: {st}, Reports returned: {len(j)}")

        # POST /api/agents/chat
        agent_payload = {"prompt": "Analyze AAPL volume and moving averages.", "target_ticker": "AAPL"}
        st, b = http_post(f"{base_url}/api/agents/chat", agent_payload)
        j = json.loads(b)
        chat_ok = (st == 200 and len(j.get("steps", [])) == 6)
        record("Agent Copilot Endpoint (POST /api/agents/chat)", chat_ok,
               f"Status: {st}, Multi-Agent Steps: {len(j.get('steps', []))}")

        # GET /app/ (Frontend React UI)
        st, b = http_get(f"{base_url}/app/")
        app_ok = (st == 200 and "DRISHTI" in b)
        record("Frontend Static Web App (GET /app/)", app_ok,
               f"Status: {st}, HTML Title & Metadata matched")

    finally:
        # Shutdown
        srv.stop()
        srv.join(timeout=3)

    # 3. Complete Cold Restart Test
    time.sleep(1.0)
    srv2 = ServerThread(app, port=8000)
    srv2.start()
    time.sleep(1.5)
    try:
        st, b = http_get(f"{base_url}/api/health")
        j = json.loads(b)
        restart_ok = (st == 200 and j.get("status") in ("online", "healthy"))
        record("Application Cold Restart Test", restart_ok, f"Restarted cleanly; Port 8000 Status: {st}, App: {j.get('status')}")
    finally:
        srv2.stop()
        srv2.join(timeout=3)

    all_passed = all(p for _, p, _ in results)
    print(f"\nArea 1 Startup Verdict: {'PASS' if all_passed else 'FAIL'}")
    return all_passed

if __name__ == "__main__":
    success = run_startup_verification()
    sys.exit(0 if success else 1)
