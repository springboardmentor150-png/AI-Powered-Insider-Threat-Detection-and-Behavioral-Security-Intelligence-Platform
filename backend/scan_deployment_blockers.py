import os
import re

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

print("=" * 70)
print("ITBIS — DEPLOYMENT BLOCKER & CONFIGURATION SCANNER")
print("=" * 70)

findings = []

PATTERNS = [
    (r"localhost", "LOCALHOST_REFERENCE"),
    (r"127\.0\.0\.1", "LOOPBACK_IP_REFERENCE"),
    (r"AdminPassword123!", "DEFAULT_TEST_PASSWORD"),
    (r"AnalystPassword123!", "DEFAULT_TEST_PASSWORD"),
    (r"itbis-development-secret-key", "DEFAULT_DEV_JWT_SECRET"),
    (r"allow_origins\s*=\s*\[\s*['\"]\*['\"]\s*\]", "UNSAFE_CORS_WILDCARD"),
]

IGNORE_DIRS = {".git", ".next", "node_modules", "venv", "__pycache__", ".system_generated"}

for root, dirs, files in os.walk(ROOT_DIR):
    dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
    for file in files:
        if file.endswith((".py", ".ts", ".tsx", ".js", ".json", ".env", ".env.local", ".env.example", ".md")):
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, ROOT_DIR)
            
            # Skip test files and verification scripts from blocker classification
            is_test_file = "test_" in file or "verify_" in file or "scan_" in file or file.endswith(".md") or ".env.example" in file
            
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    for line_num, line in enumerate(f, 1):
                        for pattern, p_type in PATTERNS:
                            if re.search(pattern, line):
                                classification = "SAFE LOCAL CONFIG" if (
                                    "os.getenv" in line or 
                                    "os.environ" in line or 
                                    "NEXT_PUBLIC_API_URL" in line or 
                                    is_test_file or 
                                    "seed" in rel_path or 
                                    ".env" in file or 
                                    "demo" in line.lower() or 
                                    "placeholder" in line.lower() or
                                    "default_origins" in line or
                                    "localhost:27017" in line
                                ) else "POTENTIAL PRODUCTION CONCERN"
                                
                                findings.append({
                                    "file": rel_path,
                                    "line": line_num,
                                    "type": p_type,
                                    "content": line.strip()[:100],
                                    "classification": classification
                                })
            except Exception as e:
                pass

print(f"Total findings scanned: {len(findings)}\n")

safe_count = 0
concern_count = 0

for item in findings:
    if item["classification"] == "SAFE LOCAL CONFIG":
        safe_count += 1
    else:
        concern_count += 1
        print(f"[{item['classification']}] {item['file']}:{item['line']} -> {item['type']}")
        print(f"  Snippet: {item['content']}\n")

print("-" * 70)
print(f"SUMMARY: {safe_count} Safe Local/Test configurations, {concern_count} Potential Production Concerns")
print("-" * 70)
