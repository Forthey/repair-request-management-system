import redis.asyncio as redis

from config import settings

pool = redis.ConnectionPool.from_url(f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}")
