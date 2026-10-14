from app.main import app
import inspect

targets = {
    "create_incident",
    "assign_alert",
    "resolve_alert",
}

for name in targets:
    function = getattr(
        __import__("app.main", fromlist=[name]),
        name,
        None,
    )

    print(f"\n=== {name} ===")

    if function is None:
        print("Function not found under this name.")
    else:
        print(inspect.getsource(function))
