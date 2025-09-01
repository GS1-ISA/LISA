import os
import time
from typing import Optional, Tuple

import jwt

SECRET = os.getenv("ISA_AUTH_SECRET", "dev-secret-change-me")
ALG = "HS256"
ADMIN_USER = os.getenv("ISA_ADMIN_USER", "admin")
ADMIN_PASS = os.getenv("ISA_ADMIN_PASS", "admin")
USER_USER = os.getenv("ISA_USER_USER", "user")
USER_PASS = os.getenv("ISA_USER_PASS", "user")


def verify_credentials(username: str, password: str) -> Optional[str]:
    if username == ADMIN_USER and password == ADMIN_PASS:
        return "admin"
    if username == USER_USER and password == USER_PASS:
        return "user"
    return None


def create_token(username: str, role: str, exp_seconds: int = 86400) -> str:
    now = int(time.time())
    payload = {"sub": username, "role": role, "iat": now, "exp": now + exp_seconds}
    return jwt.encode(payload, SECRET, algorithm=ALG)


def decode_token(token: str) -> Tuple[bool, dict]:
    try:
        data = jwt.decode(token, SECRET, algorithms=[ALG])
        return True, data
    except Exception as e:
        return False, {"error": str(e)}
