import jwt
import os
from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

bearer = HTTPBearer()
PUBLIC_KEY_PATH = os.getenv("JWT_PUBLIC_KEY_PATH", "./public.pem")
JWT_ALGORITHM = "RS256"

# In-memory revocation list (replace with Redis or DB in prod)
revoked_tokens = set()

def load_public_key():
    with open(PUBLIC_KEY_PATH, "rb") as f:
        return f.read()

def verify_token(credentials: HTTPAuthorizationCredentials = bearer):
    token = credentials.credentials
    if token in revoked_tokens:
        raise HTTPException(status_code=403, detail="Token has been revoked")

    try:
        payload = jwt.decode(token, load_public_key(), algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=403, detail="Invalid token")

def revoke_token(token: str):
    revoked_tokens.add(token)
