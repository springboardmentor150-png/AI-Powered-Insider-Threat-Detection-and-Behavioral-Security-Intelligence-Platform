from fastapi.testclient import TestClient
from app.main import app
from app.services.auth_service import create_access_token

client = TestClient(app)
token = create_access_token({"sub": "admin@itbis.cyber", "role": "admin"})
headers = {"Authorization": f"Bearer {token}"}

print("=== 1. Test default 30d ===")
res = client.get("/activity-logs/timeline", headers=headers)
assert res.status_code == 200, f"Status {res.status_code}: {res.text}"
data = res.json()
assert "items" in data and "total" in data
print(f"[PASS] Default Timeline items: {len(data['items'])} / {data['total']}")

first = data['items'][0]
print(f"[PASS] Sample item keys: {list(first.keys())}")
print(f"       Sample item data: id={first['id']}, emp={first['employee_id']}, event={first['event_type']}, sev={first['severity']}, is_anomaly={first['is_anomaly']}, why={first['why_suspicious']}")

print("=== 2. Test 24h filter ===")
res_24h = client.get("/activity-logs/timeline?time_range=24h", headers=headers)
print(f"[PASS] 24H: {len(res_24h.json()['items'])} items")

print("=== 3. Test 7d filter ===")
res_7d = client.get("/activity-logs/timeline?time_range=7d", headers=headers)
print(f"[PASS] 7D: {len(res_7d.json()['items'])} items")

print("=== 4. Test Employee filter ===")
for emp in ['CYB-1042', 'FIN-2187', 'IT-3064', 'HR-4128', 'DEV-5271', 'CMP-6385']:
    res_emp = client.get(f"/activity-logs/timeline?employee_id={emp}", headers=headers)
    assert res_emp.status_code == 200
    items = res_emp.json()['items']
    assert all(i['employee_id'] == emp for i in items)
    print(f"[PASS] Employee {emp}: {len(items)} items")

print("=== 5. Test Event Type filter ===")
for evt in ['file_download', 'usb_connect', 'privilege_change', 'login', 'data_transfer']:
    res_evt = client.get(f"/activity-logs/timeline?event_type={evt}", headers=headers)
    assert res_evt.status_code == 200
    items = res_evt.json()['items']
    assert all(i['event_type'] == evt for i in items)
    print(f"[PASS] Event Type {evt}: {len(items)} items")

print("=== 6. Test Unauthorized ===")
res_unauth = client.get("/activity-logs/timeline")
assert res_unauth.status_code == 401
print("[PASS] Unauthorized 401 verified")
print("=== ALL TESTS SUCCEEDED ===")
