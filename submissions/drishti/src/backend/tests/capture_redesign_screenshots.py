"""
DRISHTI — Premium Monochrome Redesign Visual Capture Suite
Captures high-resolution screenshots for all 8 application views and logo variations.
"""
import os
import sys
import time
import subprocess
import threading
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

class ServerThread(threading.Thread):
    def __init__(self, app, host="127.0.0.1", port=8000):
        super().__init__()
        self.server = uvicorn.Server(uvicorn.Config(app, host=host, port=port, log_level="warning"))
        self.daemon = True

    def run(self):
        self.server.run()

    def stop(self):
        self.server.should_exit = True

def capture_all():
    print("=" * 75)
    print("  DRISHTI — CAPTURING PREMIUM MONOCHROME REDESIGN SCREENSHOTS")
    print("=" * 75)

    browser_bin = None
    for c in [r"C:\Program Files\Google\Chrome\Application\chrome.exe", r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"]:
        if os.path.exists(c):
            browser_bin = c
            break

    if not browser_bin:
        print("[-] Error: Chrome or Edge executable not found.")
        return False

    out_dir = os.path.join(base_dir, "frontend", "screenshots")
    os.makedirs(out_dir, exist_ok=True)

    # 1. Capture Master Logo Showcase
    logo_html_path = os.path.join(out_dir, "logo_showcase.html")
    logo_shot_path = os.path.join(out_dir, "drishti_logo_showcase.png")
    cmd_logo = [
        browser_bin,
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--window-size=1400,900",
        f"--screenshot={logo_shot_path}",
        f"file:///{logo_html_path.replace(os.sep, '/')}"
    ]
    subprocess.run(cmd_logo, capture_output=True, timeout=10)
    logo_ok = os.path.exists(logo_shot_path) and os.path.getsize(logo_shot_path) > 10000
    print(f"  [+] Brand Identity Logo Showcase: {'CAPTURED' if logo_ok else 'FAILED'} ({os.path.getsize(logo_shot_path)//1024} KB)")

    # 2. Boot Application Server
    srv = ServerThread(app, port=8000)
    srv.start()
    time.sleep(2.0)

    views = [
        ("01_Market_Overview", "http://127.0.0.1:8000/app/?tab=dashboard", "1440,900", "drishti_01_market_overview.png"),
        ("02_Volume_Intelligence", "http://127.0.0.1:8000/app/?tab=stocks", "1440,900", "drishti_02_volume_intelligence.png"),
        ("03_Anomaly_Detection", "http://127.0.0.1:8000/app/?tab=anomalies", "1440,900", "drishti_03_anomaly_detection.png"),
        ("04_Sector_Intelligence", "http://127.0.0.1:8000/app/?tab=sectors", "1440,900", "drishti_04_sector_intelligence.png"),
        ("05_AI_Copilot", "http://127.0.0.1:8000/app/?tab=copilot", "1440,900", "drishti_05_ai_copilot.png"),
        ("06_Reports_History", "http://127.0.0.1:8000/app/?tab=reports", "1440,900", "drishti_06_reports_history.png"),
        ("07_Data_Ingestion", "http://127.0.0.1:8000/app/?tab=ingestion", "1440,900", "drishti_07_data_ingestion.png"),
        ("08_Settings_Db2", "http://127.0.0.1:8000/app/?tab=settings", "1440,900", "drishti_08_settings_db2.png"),
        ("Responsive_Tablet", "http://127.0.0.1:8000/app/?tab=dashboard", "768,1024", "drishti_tablet_responsive.png"),
        ("Responsive_Mobile", "http://127.0.0.1:8000/app/?tab=dashboard", "375,812", "drishti_mobile_responsive.png"),
    ]

    try:
        for name, url, dimensions, filename in views:
            shot_file = os.path.join(out_dir, filename)
            cmd = [
                browser_bin,
                "--headless=new",
                "--disable-gpu",
                "--no-sandbox",
                f"--window-size={dimensions}",
                f"--screenshot={shot_file}",
                url
            ]
            subprocess.run(cmd, capture_output=True, timeout=12)
            shot_ok = os.path.exists(shot_file) and os.path.getsize(shot_file) > 10000
            size_kb = os.path.getsize(shot_file) // 1024 if os.path.exists(shot_file) else 0
            print(f"  [+] {name} ({dimensions}): {'CAPTURED' if shot_ok else 'FAILED'} ({size_kb} KB)")
    finally:
        srv.stop()
        srv.join(timeout=3)

    print("\n[+] Visual Capture Complete. All artifacts saved to frontend/screenshots/")
    return True

if __name__ == "__main__":
    success = capture_all()
    sys.exit(0 if success else 1)

