from app.dependencies import require_role
from app.models import User, Incident, InvestigationNote
import inspect

print("=== require_role definition ===")
print(inspect.getsource(require_role))

print("\n=== User model columns ===")
print(list(User.__table__.columns.keys()))

print("\n=== Current incident-related imports and routes ===")
with open("app/main.py", "r", encoding="utf-8-sig") as file:
    lines = file.readlines()

for index, line in enumerate(lines):
    if (
        "from app.schemas import" in line
        or "from app.models import" in line
        or '@app.post("/incidents"' in line
        or '@app.get("/incidents' in line
        or '@app.patch("/incidents' in line
    ):
        start = max(0, index - 1)
        end = min(len(lines), index + 5)
        print(f"\n--- Lines {start + 1}-{end} ---")
        print("".join(lines[start:end]))
