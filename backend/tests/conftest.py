import pytest
import asyncio
import uuid
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from redis.asyncio import Redis

from app.core.config import settings
from app.core.database import Base, get_db
from app.core.redis import get_redis
from app.core.security import generate_api_key
from app.models.tenant import Tenant
from app.main import app

# Test database URL (SQLite in-memory)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def async_session() -> AsyncGenerator[AsyncSession, None]:
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def mock_redis(mocker):
    """Mock Redis client for tests that don't need live Redis."""
    redis = mocker.AsyncMock(spec=Redis)
    redis.xadd = mocker.AsyncMock(return_value="12345-0")
    redis.publish = mocker.AsyncMock(return_value=1)
    
    # Mock Lua script execution
    mock_lua_script = mocker.AsyncMock(return_value=[1, 0.0])
    redis.register_script = mocker.MagicMock(return_value=mock_lua_script)
    return redis


@pytest.fixture
async def test_tenant(async_session: AsyncSession) -> tuple[Tenant, str]:
    raw_key, hashed_key = generate_api_key(prefix="nds_test_")
    tenant = Tenant(
        id=uuid.uuid4(),
        name="Test Suite Tenant",
        api_key_hash=hashed_key,
        rate_limit_rps=10  # Adequate limit for tests
    )
    async_session.add(tenant)
    await async_session.commit()
    await async_session.refresh(tenant)
    return tenant, raw_key


@pytest.fixture
async def client(async_session: AsyncSession, mock_redis) -> AsyncGenerator[AsyncClient, None]:
    async def _get_test_db():
        yield async_session

    async def _get_test_redis():
        yield mock_redis

    app.dependency_overrides[get_db] = _get_test_db
    app.dependency_overrides[get_redis] = _get_test_redis

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
