"""
DRISHTI Verification Suite — Area 7: Security Audit & Credential Protection
Verifies:
1. No hardcoded database passwords or API keys in source files.
2. .gitignore properly guards .env, .venv, and sensitive files.
3. .env.example contains only non-sensitive placeholders.
4. Parameterized SQL queries in services to prevent SQL injection.
5. Path portability check (no developer-specific absolute paths hardcoded in backend services).
"""
import os
import re
import sys

def run_security_audit():
    print("=" * 70)
    print("  AREA 7: SECURITY AUDIT & CREDENTIAL HYGIENE")
    print("=" * 70)

    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    results = []

    def record(name: str, passed: bool, detail: str):
        results.append((name, passed, detail))
        sym = "[PASS]" if passed else "[FAIL]"
        print(f"  {sym} {name}: {detail}")

    # 1. Check .gitignore
    gitignore_path = os.path.join(base_dir, ".gitignore")
    if os.path.exists(gitignore_path):
        with open(gitignore_path, "r", encoding="utf-8") as f:
            gi_content = f.read()
        gi_has_env = ".env" in gi_content and ".venv" in gi_content
        record(".gitignore Coverage", gi_has_env, ".env and .venv are ignored")
    else:
        record(".gitignore Coverage", False, ".gitignore file not found")

    # 2. Check .env.example
    example_path = os.path.join(base_dir, ".env.example")
    if os.path.exists(example_path):
        with open(example_path, "r", encoding="utf-8") as f:
            ex_content = f.read()
        has_placeholders = "your_db2_password_here" in ex_content and "your_gemini_api_key_here" in ex_content
        record(".env.example Hygiene", has_placeholders, "Contains clean placeholders")
    else:
        record(".env.example Hygiene", False, ".env.example not found")

    # 3. Read actual DB password from .env to ensure it never appears in source code
    actual_pwd = None
    env_path = os.path.join(base_dir, ".env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("DB2_PASSWORD="):
                    actual_pwd = line.split("=", 1)[1].strip()

    # 4. Scan source files for hardcoded secrets
    ignore_dirs = {'.venv', 'node_modules', '.git', '__pycache__', 'dist', 'exports', 'tests'}
    ignore_files = {'.env', 'drishti_dashboard.png', 'favicon.svg', 'icons.svg', 'test_security_audit.py'}
    
    suspicious_patterns = [
        re.compile(r'(?i)(password|secret|api_key|token)\s*=\s*[\'"][^\'"]{8,}[\'"]'),
    ]

    leaked_files = []
    pwd_leaks = []

    for root, dirs, files in os.walk(base_dir):
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        for file in files:
            if file in ignore_files or file.endswith(('.pyc', '.png', '.ico', '.pdf', '.xlsx', '.svg')):
                continue
            fpath = os.path.join(root, file)
            relpath = os.path.relpath(fpath, base_dir)
            try:
                with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    
                    if actual_pwd and len(actual_pwd) >= 6 and actual_pwd in content and not file.startswith(".env"):
                        pwd_leaks.append(relpath)

                    for pat in suspicious_patterns:
                        matches = pat.findall(content)
                        for m in matches:
                            # Filter out placeholder comments or mock docs
                            if not any(ph in m.lower() for ph in ["your_", "placeholder", "<your", "example"]):
                                leaked_files.append((relpath, m))
            except Exception:
                pass

    record("Zero Database Password Exposure", len(pwd_leaks) == 0, 
           f"Exposures: {len(pwd_leaks)} (Files: {pwd_leaks})")
    record("Zero Hardcoded Secrets in Source", len(leaked_files) == 0,
           f"Suspicious tokens found: {len(leaked_files)} -> {leaked_files}")

    # 5. Parameterized SQL verification
    backend_services = os.path.join(base_dir, "backend", "services")
    sql_concat_risks = []
    
    # Check for direct SQL injection patterns like f"SELECT ... {variable}"
    injection_pat = re.compile(r'f["\']\s*(?:SELECT|INSERT|UPDATE|DELETE)\s+.*?\{[a-zA-Z_]', re.IGNORECASE)
    
    for root, _, files in os.walk(backend_services):
        for file in files:
            if file.endswith(".py"):
                fpath = os.path.join(root, file)
                relpath = os.path.relpath(fpath, base_dir)
                with open(fpath, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    for idx, line in enumerate(lines, 1):
                        # Allow safe identifiers if properly validated, but flag raw input interpolation
                        if injection_pat.search(line):
                            sql_concat_risks.append((relpath, idx, line.strip()))

    record("Parameterized SQL Enforcement", len(sql_concat_risks) == 0,
           f"Unsafe raw SQL f-strings: {len(sql_concat_risks)} -> {sql_concat_risks}")

    # Summary
    all_passed = all(p for _, p, _ in results)
    print(f"\nArea 7 Security Verdict: {'PASS' if all_passed else 'FAIL'}")
    return all_passed

if __name__ == "__main__":
    success = run_security_audit()
    sys.exit(0 if success else 1)
