from app.main import app

required_routes = {
    ("GET", "/incidents"),
    ("POST", "/incidents/{incident_id}/notes"),
    ("GET", "/incidents/{incident_id}/notes"),
    ("PATCH", "/incidents/{incident_id}/resolve"),
}

registered_routes = set()

for route in app.routes:
    if hasattr(route, "methods") and hasattr(route, "path"):
        for method in route.methods:
            registered_routes.add((method, route.path))

for method, path in sorted(required_routes):
    status = "PASS" if (method, path) in registered_routes else "MISSING"
    print(f"{status}: {method} {path}")

missing = required_routes - registered_routes

if missing:
    raise SystemExit("\nSome incident endpoints are missing.")

print("\nAll four incident endpoints are registered.")
