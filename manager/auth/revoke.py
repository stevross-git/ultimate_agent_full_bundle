from fastapi import APIRouter, Request
from manager.auth.validator import revoke_token
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter()
bearer = HTTPBearer()

@router.post("/auth/revoke")
def revoke(credentials: HTTPAuthorizationCredentials = bearer):
    token = credentials.credentials
    revoke_token(token)
    return {"message": "Token revoked"}
