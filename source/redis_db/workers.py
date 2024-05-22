from redis.asyncio import Redis

from redis_db.base import pool

from database.queries.workers import get_workers
from schemas.workers import Worker


async def load_workers():
    redis: Redis
    async with Redis(connection_pool=pool) as redis:
        workers: list[Worker] = await get_workers()

        pipe = redis.pipeline()
        for worker in workers:
            await pipe.set(f"user:{worker.telegram_id}", worker.access_right)

        await pipe.execute()


async def check_common_access(telegram_id: int) -> bool:
    redis_client: Redis
    async with Redis(connection_pool=pool) as redis_client:
        return (await redis_client.get(f"user:{telegram_id}")) is not None


async def check_admin_rights(telegram_id: int) -> bool:
    redis_client: Redis
    async with Redis(connection_pool=pool) as redis_client:
        return (await redis_client.get(f"user:{telegram_id}")) == "admin"
