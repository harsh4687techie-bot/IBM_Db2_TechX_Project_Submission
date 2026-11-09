"""
DRISHTI Verification Suite — Area 9: Path Portability & Environment Cleanliness
Verifies:
1. No developer-specific absolute paths hardcoded in backend services, models, routers, core.
2. Frontend Vite build is self-contained with relative assets base path './'.
3. Python virtual environment contains required packages (ibm-db, fastapi, uvicorn, pandas, reportlab, openpyxl).
"""
import os
import sys
import re

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

def run_portability_verification():
    print("=" * 70)
    print("  AREA 9: PATH PORTABILITY & BUILD CLEANLINESS VERIFICATION")
    print("=" * 70)

    results = []
    def record(name: str, passed: bool, detail: str):
        results.append((name, passed, detail))
        sym = "[PASS]" if passed else "[FAIL]"
        print(f"  {sym} {name}: {detail}")

    # 1. Check for hardcoded user paths in backend source code
    user_path_pattern = re.compile(r'C:\\Users\\[a-zA-Z0-9_\-\.]+', re.IGNORECASE)
    hardcoded_user_paths = []

    backend_dir = os.path.join(base_dir, "backend")
    for root, dirs, files in os.walk(backend_dir):
        if "tests" in dirs:
            dirs.remove("tests")
        if "__pycache__" in dirs:
            dirs.remove("__pycache__")
        for file in files:
            if file.endswith(".py"):
                fpath = os.path.join(root, file)
                relpath = os.path.relpath(fpath, base_dir)
                with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    matches = user_path_pattern.findall(content)
                    if matches:
                        hardcoded_user_paths.append((relpath, matches))

    record("Zero Hardcoded Absolute User Paths in Backend", len(hardcoded_user_paths) == 0,
           f"Violations: {len(hardcoded_user_paths)} (Files: {hardcoded_user_paths})")

    # 2. Check frontend Vite base path in vite.config.ts
    vite_config_path = os.path.join(base_dir, "frontend", "vite.config.ts")
    has_relative_base = False
    if os.path.exists(vite_config_path):
        with open(vite_config_path, "r", encoding="utf-8") as f:
            cfg = f.read()
            has_relative_base = ("base: './'" in cfg or 'base: "./"' in cfg)
    record("Frontend Portable Base Path (./)", has_relative_base, "Vite configured with base: './' for clean static asset serving")

    # 3. Check dist/index.html assets linkage
    dist_html_path = os.path.join(base_dir, "frontend", "dist", "index.html")
    dist_ok = False
    if os.path.exists(dist_html_path):
        with open(dist_html_path, "r", encoding="utf-8") as f:
            html = f.read()
            # Verify relative asset references
            dist_ok = ('./assets/' in html or 'href="./' in html or 'src="./' in html)
    record("Frontend Distribution Linkage", dist_ok, "Production index.html links relative assets cleanly")

    # 4. Check core Python packages in environment
    required_packages = ["ibm_db", "fastapi", "uvicorn", "pandas", "reportlab", "openpyxl"]
    missing_packages = []
    for pkg in required_packages:
        try:
            __import__(pkg)
        except ImportError:
            missing_packages.append(pkg)
    record("Core Python Dependency Availability", len(missing_packages) == 0,
           f"All packages present: {required_packages}")

    all_passed = all(p for _, p, _ in results)
    print(f"\nArea 9 Portability Verdict: {'PASS' if all_passed else 'FAIL'}")
    return all_passed

if __name__ == "__main__":
    success = run_portability_verification()
    sys.exit(0 if success else 1)

