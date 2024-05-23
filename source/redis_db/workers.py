from redis.asyncio import Redis

from redis_db.base import pool

from database.queries.workers import get_workers, get_worker
from schemas.workers import Worker


async def load_workers():
    redis: Redis
    async with Redis(connection_pool=pool) as redis:
        workers: list[Worker] = await get_workers()

        pipe = redis.pipeline()
        for worker in workers:
            await pipe.set(f"user:{worker.telegram_id}", worker.access_right)

        await pipe.execute()


async def reload_worker(telegram_id: int):
    redis: Redis
    async with Redis(connection_pool=pool) as redis:
        worker: Worker = await get_worker(telegram_id, True)
        if not worker.active:
            await redis.delete(f"user:{telegram_id}")
            return
        await redis.set(f"user:{telegram_id}", worker.access_right)


async def check_common_access(telegram_id: int) -> bool:
    redis_client: Redis
    async with Redis(connection_pool=pool) as redis_client:
        return await redis_client.exists(f"user:{telegram_id}")


async def check_admin_rights(telegram_id: int) -> bool:
    redis_client: Redis
    async with Redis(connection_pool=pool) as redis_client:
        return (await redis_client.get(f"user:{telegram_id}")).decode("utf-8") == "Админ"
