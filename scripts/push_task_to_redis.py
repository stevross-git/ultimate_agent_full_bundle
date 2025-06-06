import asyncio
import aioredis
import uuid
import json
import os

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
STREAM_KEY = "agent:tasks"

async def push_task(redis, task_payload: dict):
    task_id = str(uuid.uuid4())
    fields = {
        "task_id": task_id,
        "payload": json.dumps(task_payload)
    }
    await redis.xadd(STREAM_KEY, fields)
    print(f"✅ Pushed task {task_id} to stream")

async def main():
    redis = await aioredis.from_url(REDIS_URL)
    for i in range(3):
        await push_task(redis, {"type": "compute", "job": f"task-{i+1}"})
    await redis.close()

if __name__ == "__main__":
    asyncio.run(main())
