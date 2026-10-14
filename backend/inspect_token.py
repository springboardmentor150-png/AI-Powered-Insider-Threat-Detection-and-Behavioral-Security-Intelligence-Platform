from app.dependencies import decode_access_token
import inspect

print("=== Token decoder ===")
print(inspect.getsource(decode_access_token))

print("\n=== Token creation and login references ===")
with open("app/main.py", "r", encoding="utf-8-sig") as file:
    lines = file.readlines()

for index, line in enumerate(lines):
    if any(term in line.lower() for term in [
        "create_access_token",
        "decode_access_token",
        "token_data",
        "access_token"
    ]):
        start = max(0, index - 2)
        end = min(len(lines), index + 5)
        print(f"\n--- Lines {start + 1}-{end} ---")
        print("".join(lines[start:end]))
