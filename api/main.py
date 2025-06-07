from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import os
import aioredis
import uuid
import json
import jwt

app = FastAPI()
bearer = HTTPBearer()
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
STREAM_KEY = "agent:tasks"
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key")

class TaskPayload(BaseModel):
    type: str
    job: str

class CommandPayload(BaseModel):
    command: str
    params: dict | None = None

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(bearer)):
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=["HS256"])
        return payload
    except jwt.PyJWTError:
        raise HTTPException(status_code=403, detail="Invalid token")

@app.post("/task")
async def post_task(task: TaskPayload, token_data: dict = Depends(verify_token)):
    redis = await aioredis.from_url(REDIS_URL)
    task_id = str(uuid.uuid4())
    await redis.xadd(STREAM_KEY, {
        "task_id": task_id,
        "payload": json.dumps(task.dict())
    })
    await redis.close()
    return {"message": "Task submitted", "task_id": task_id}


@app.post("/command")
async def post_command(cmd: CommandPayload, token_data: dict = Depends(verify_token)):
    redis = await aioredis.from_url(REDIS_URL)
    await redis.publish("agent:control", json.dumps(cmd.dict()))
    await redis.close()
    return {"message": "Command dispatched"}
