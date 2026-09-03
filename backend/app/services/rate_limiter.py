import time
import logging
import redis.asyncio as aioredis

logger = logging.getLogger(__name__)

# Atomic Token Bucket Lua Script
# KEYS[1]: rate limiter Redis key (e.g. "rate_limit:tenant:<tenant_id>" or "rate_limit:provider:global")
# ARGV[1]: rate (tokens added per second, e.g. 10.0)
# ARGV[2]: capacity (max token bucket capacity, e.g. 10.0)
# ARGV[3]: requested (tokens requested, usually 1.0)
# ARGV[4]: now (current unix timestamp in seconds float)
TOKEN_BUCKET_LUA_SCRIPT = """
local key = KEYS[1]
local rate = tonumber(ARGV[1])
local capacity = tonumber(ARGV[2])
local requested = tonumber(ARGV[3])
local now = tonumber(ARGV[4])

-- Retrieve current state [tokens, last_updated]
local data = redis.call('HMGET', key, 'tokens', 'last_updated')
local tokens = tonumber(data[1])
local last_updated = tonumber(data[2])

if tokens == nil or last_updated == nil then
    -- Initial state: bucket full
    tokens = capacity
    last_updated = now
else
    -- Refill tokens based on time elapsed
    local delta = math.max(0, now - last_updated)
    tokens = math.min(capacity, tokens + (delta * rate))
    last_updated = now
end

-- Check if enough tokens available
if tokens >= requested then
    tokens = tokens - requested
    redis.call('HMSET', key, 'tokens', tokens, 'last_updated', last_updated)
    -- Set TTL to prevent stale key leak (e.g. 60 seconds)
    redis.call('EXPIRE', key, 60)
    return {1, 0} -- {allowed (1), retry_after (0)}
else
    -- Denied: compute retry_after wait duration in seconds
    local needed = requested - tokens
    local retry_after = needed / rate
    return {0, retry_after} -- {allowed (0), retry_after}
end
"""


class RedisRateLimiter:
    """
    Reusable, concurrency-safe Token Bucket Rate Limiter backed by Redis Lua scripting.
    """

    def __init__(self, redis_client: aioredis.Redis):
        self.redis = redis_client
        self._script = self.redis.register_script(TOKEN_BUCKET_LUA_SCRIPT)

    async def is_allowed(
        self,
        identifier: str,
        rate: float,
        capacity: float | None = None,
        requested: int = 1
    ) -> tuple[bool, float]:
        """
        Check if request is allowed under the token bucket algorithm.
        Returns tuple: (is_allowed: bool, retry_after_seconds: float)
        """
        if capacity is None:
            capacity = rate  # Default capacity equals 1-second burst rate

        key = f"rate_limit:{identifier}"
        now = time.time()

        try:
            result = await self._script(
                keys=[key],
                args=[rate, capacity, requested, now]
            )
            allowed = bool(result[0] == 1)
            retry_after = float(result[1])
            return allowed, retry_after
        except Exception as e:
            logger.error(f"Rate limiter script execution error for key {key}: {str(e)}", exc_info=True)
            # Fail open in emergency Redis error so traffic is not permanently blocked
            return True, 0.0
