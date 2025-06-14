from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import os
import aioredis
import uuid
import json
import jwt
import platform
import psutil
from typing import Any, Dict

from ultimate_agent import get_available_modules, get_version
from ultimate_agent.config.config_settings import ConfigManager
from ultimate_agent.storage.database.migrations import DatabaseManager
from ultimate_agent.ai.models.ai_models import AIModelManager
from ultimate_agent.blockchain.wallet.security import BlockchainManager

app = FastAPI()
bearer = HTTPBearer()
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
STREAM_KEY = "agent:tasks"
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key")

# Lazily initialized managers
_config_manager: ConfigManager | None = None
_database_manager: DatabaseManager | None = None
_ai_manager: AIModelManager | None = None
_blockchain_manager: BlockchainManager | None = None


def get_config_manager() -> ConfigManager:
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


def get_database_manager() -> DatabaseManager:
    global _database_manager
    if _database_manager is None:
        cfg = get_config_manager()
        db_path = cfg.get('DATABASE', 'path', './ultimate_agent.db')
        _database_manager = DatabaseManager(db_path)
    return _database_manager


def get_ai_manager() -> AIModelManager:
    global _ai_manager
    if _ai_manager is None:
        cfg = get_config_manager()
        _ai_manager = AIModelManager(cfg)
    return _ai_manager


def get_blockchain_manager() -> BlockchainManager:
    global _blockchain_manager
    if _blockchain_manager is None:
        cfg = get_config_manager()
        _blockchain_manager = BlockchainManager(cfg)
    return _blockchain_manager

class TaskPayload(BaseModel):
    type: str
    job: str

class CommandPayload(BaseModel):
    command: str
    params: dict | None = None

class InferenceRequest(BaseModel):
    model: str
    input: str

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


# ---------------------------------------------------------------------------
# Additional API endpoints mirroring the enhanced_node Flask server. These
# endpoints now integrate with the real modules included in this repository.
# ---------------------------------------------------------------------------

@app.get("/api/stats")
async def get_stats():
    """Return basic agent statistics from the database."""
    db = get_database_manager()
    return db.load_agent_stats()


@app.get("/api/v3/stats/enhanced")
async def get_enhanced_stats():
    """Return enhanced statistics including database info."""
    db = get_database_manager()
    stats = db.load_agent_stats()
    db_stats = db.get_database_stats()
    return {
        "status": "online",
        "version": get_version(),
        "stats": stats,
        "database": db_stats,
    }


@app.get("/api/system")
async def get_system():
    """Return simple system information."""
    return {
        "cpu_percent": psutil.cpu_percent(),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage("/").percent,
        "platform": platform.system(),
    }


@app.get("/api/capabilities")
async def get_capabilities():
    """Return agent capability information."""
    caps = get_available_modules()
    caps["api_version"] = "v4"
    return caps


@app.post("/api/start_task")
async def api_start_task(task: TaskPayload, token_data: dict = Depends(verify_token)):
    """Alias for /task."""
    return await post_task(task, token_data)


@app.get("/api/tasks")
async def get_tasks(token_data: dict = Depends(verify_token)):
    """Return tasks stored in Redis."""
    redis = await aioredis.from_url(REDIS_URL)
    msgs = await redis.xrevrange(STREAM_KEY, count=20)
    await redis.close()
    tasks = []
    for msg_id, fields in msgs:
        entry = {k.decode(): v.decode() for k, v in fields.items()}
        entry["id"] = msg_id.decode() if isinstance(msg_id, bytes) else msg_id
        tasks.append(entry)
    return {"tasks": tasks}


@app.post("/api/cancel_task/{task_id}")
async def cancel_task(task_id: str, token_data: dict = Depends(verify_token)):
    """Cancel a task by ID via Redis message."""
    redis = await aioredis.from_url(REDIS_URL)
    await redis.publish("agent:control", json.dumps({"command": "cancel", "task_id": task_id}))
    await redis.close()
    return {"cancelled": True, "task_id": task_id}


@app.get("/api/v3/ai/capabilities")
async def ai_capabilities():
    """Return AI capabilities from the AI manager."""
    manager = get_ai_manager()
    return manager.get_model_stats()


@app.get("/api/training")
async def get_training():
    """Return training summary from the database."""
    db = get_database_manager()
    return db.get_ai_training_summary()


@app.post("/api/ai/inference")
async def ai_inference(req: InferenceRequest, token_data: dict = Depends(verify_token)):
    """Perform AI inference using the AI manager."""
    manager = get_ai_manager()
    result = manager.run_inference(req.model, req.input)
    return result


@app.get("/api/blockchain/balance")
async def blockchain_balance():
    """Return blockchain balance."""
    bc = get_blockchain_manager()
    return bc.get_balance()


@app.get("/api/blockchain/transactions")
async def blockchain_transactions():
    """Return blockchain transactions."""
    bc = get_blockchain_manager()
    return {"transactions": bc.get_transaction_history(20)}


@app.get("/api/performance/metrics")
async def performance_metrics():
    """Return performance metrics from the database."""
    db = get_database_manager()
    return {"metrics": db.get_performance_metrics(24)}


@app.get("/api/database/stats")
async def database_stats():
    """Return database statistics."""
    db = get_database_manager()
    return db.get_database_stats()


@app.get("/api/health")
async def health_check():
    """Simple health check endpoint."""
    return {"status": "healthy"}
