from app.jwt_auth import create_access_token
from app.dependencies import decode_access_token

token = create_access_token(user_id=123, role="security_analyst")
payload = decode_access_token(token)

print("Decoded token payload:", payload)
print("user_id:", payload.get("user_id"))
print("sub:", payload.get("sub"))
print("role:", payload.get("role"))
