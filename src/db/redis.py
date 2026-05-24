from typing import AsyncIterator

import redis.asyncio as redis
from redis.asyncio import Redis

from src.core.config import settings

redis_pool = redis.ConnectionPool.from_url(
    f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}"
)


async def get_redis_client() -> AsyncIterator[Redis]:
    async with redis.Redis(connection_pool=redis_pool) as client:
        yield client
