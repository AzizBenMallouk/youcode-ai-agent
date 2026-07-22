import secrets
from hashlib import sha256
from datetime import datetime, timezone, timedelta
import jwt

def create_access_token(
    *,
    user_id: str,
    email: str,
    role: str,
    secret_key: str,
    ttl_minutes: int = 15,
) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "email": email,
        "role": role,
        "iat": now,
        "exp": now + timedelta(minutes=ttl_minutes),
        "type": "access",
    }
    return jwt.encode(payload, secret_key, algorithm="HS256")

def decode_access_token(
    token: str,
    *,
    secret_key: str,
) -> dict:
    return jwt.decode(
        token,
        secret_key,
        algorithms=["HS256"],
        options={"require": ["sub", "email", "role", "exp"]},
    )

def generate_refresh_token() -> str:
    return secrets.token_urlsafe(32)

def hash_token(token: str) -> str:
    return sha256(token.encode("utf-8")).hexdigest()
