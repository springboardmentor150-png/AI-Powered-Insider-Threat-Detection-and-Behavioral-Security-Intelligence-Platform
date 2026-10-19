import os
import sys
import time
import urllib.request
import subprocess

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

python_exe = sys.executable
cwd = os.path.dirname(os.path.abspath(__file__))

print(f"Launching uvicorn app.main:app using {python_exe}...")
proc = subprocess.Popen(
    [python_exe, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"],
    cwd=cwd,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

try:
    started = False
    for i in range(25):
        time.sleep(0.5)
        try:
            with urllib.request.urlopen("http://127.0.0.1:8000/", timeout=2) as res:
                if res.getcode() == 200:
                    body = res.read().decode("utf-8")
                    print(f"GET / Response: {body}")
                    started = True
                    break
        except Exception as e:
            pass

    if not started:
        print("ERROR: uvicorn failed to start within timeout.")
        sys.exit(1)

    # Check /docs
    with urllib.request.urlopen("http://127.0.0.1:8000/docs", timeout=2) as res_docs:
        print(f"GET /docs Status: {res_docs.getcode()}")
        assert res_docs.getcode() == 200, "GET /docs failed"

    print("SUCCESS: Production-style startup verification passed!")

finally:
    proc.terminate()
    try:
        proc.wait(timeout=3)
    except Exception:
        proc.kill()
