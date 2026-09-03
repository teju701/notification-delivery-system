import redis.asyncio as aioredis
from typing import AsyncGenerator
from app.core.config import settings

# Global redis client instance
redis_client: aioredis.Redis | None = None


async def get_redis_client() -> aioredis.Redis:
    """Initialize or return existing async Redis client connection."""
    global redis_client
    if redis_client is None:
        redis_client = aioredis.from_url(
            settings.get_redis_url,
            encoding="utf-8",
            decode_responses=True
        )
    return redis_client


async def close_redis_client() -> None:
    """Close async Redis client connection on app shutdown."""
    global redis_client
    if redis_client is not None:
        await redis_client.aclose()
        redis_client = None


async def get_redis() -> AsyncGenerator[aioredis.Redis, None]:
    """Dependency injection helper for FastAPI routes."""
    client = await get_redis_client()
    yield client
