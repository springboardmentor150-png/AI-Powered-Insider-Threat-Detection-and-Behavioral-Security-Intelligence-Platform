from jose import jwt
from datetime import datetime, timedelta

SECRET_KEY = "change-this-in-production"
ALGORITHM = "HS256"

def create_token(user_id: int, role: str):
    payload = {
        "sub": str(user_id),
        "role": role,
        "exp": datetime.utcnow() + timedelta(hours=8)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str):
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])