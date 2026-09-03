import pytest
from unittest.mock import AsyncMock
from app.services.rate_limiter import RedisRateLimiter


@pytest.mark.asyncio
async def test_token_bucket_rate_limiter(mocker):
    """Unit test token bucket rate limiter logic."""
    mock_redis = mocker.AsyncMock()
    limiter = RedisRateLimiter(mock_redis)

    # 1. Allowed case mock response from Lua script: {1, 0}
    limiter._script = AsyncMock(return_value=[1, 0])

    allowed, retry_after = await limiter.is_allowed("tenant:123", rate=10.0)
    assert allowed is True
    assert retry_after == 0.0

    # 2. Exceeded case mock response from Lua script: {0, 2.5}
    limiter._script = AsyncMock(return_value=[0, 2.5])

    allowed, retry_after = await limiter.is_allowed("tenant:123", rate=10.0)
    assert allowed is False
    assert retry_after == 2.5
