from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime, timedelta
import jwt
import os

router = APIRouter()
PRIVATE_KEY_PATH = os.getenv("JWT_PRIVATE_KEY_PATH", "./private.pem")
PUBLIC_KEY_PATH = os.getenv("JWT_PUBLIC_KEY_PATH", "./public.pem")
JWT_ALGORITHM = "RS256"
JWT_EXP_MINUTES = 15

class AuthRequest(BaseModel):
    agent_id: str

def load_private_key():
    with open(PRIVATE_KEY_PATH, "rb") as f:
        return f.read()

@router.post("/auth/token")
def issue_token(auth: AuthRequest):
    try:
        payload = {
            "sub": auth.agent_id,
            "role": "agent",
            "exp": datetime.utcnow() + timedelta(minutes=JWT_EXP_MINUTES)
        }
        token = jwt.encode(payload, load_private_key(), algorithm=JWT_ALGORITHM)
        return {"access_token": token}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Token generation failed: {str(e)}")
