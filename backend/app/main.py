import asyncio
import logging
import asyncpg
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base
from app.core.redis import get_redis_client, close_redis_client
from app.api.v1.router import api_v1_router
from app.api.v1.endpoints.websockets import router as ws_router
from app.services.websocket_manager import ws_manager

# Configure structured logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s"
)
logger = logging.getLogger(__name__)


async def ensure_database_exists():
    """Ensures target database exists in PostgreSQL."""
    try:
        sys_conn = await asyncpg.connect(
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
            host=settings.POSTGRES_HOST,
            port=settings.POSTGRES_PORT,
            database="postgres"
        )
        try:
            db_exists = await sys_conn.fetchval(
                "SELECT 1 FROM pg_database WHERE datname = $1", settings.POSTGRES_DB
            )
            if not db_exists:
                logger.info(f"Database '{settings.POSTGRES_DB}' does not exist. Creating database...")
                await sys_conn.execute(f'CREATE DATABASE "{settings.POSTGRES_DB}"')
                logger.info(f"Database '{settings.POSTGRES_DB}' created successfully.")
        finally:
            await sys_conn.close()
    except Exception as e:
        logger.warning(f"Database check/creation helper notice: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI Lifespan Manager:
    - Creates database tables on startup (if not already existing via Alembic)
    - Starts Redis PubSub WebSocket background listener
    - Gracefully closes connections on shutdown
    """
    logger.info("Initializing application resources...")
    
    # Ensure database exists
    await ensure_database_exists()

    # Initialize Database Schema
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database schema verified.")

    # Initialize Redis Client and start PubSub listener
    redis = await get_redis_client()
    pubsub_task = asyncio.create_task(ws_manager.start_pubsub_listener(redis))
    logger.info("Redis PubSub listener task spawned.")

    yield

    # Cleanup
    logger.info("Shutting down application resources...")
    pubsub_task.cancel()
    try:
        await pubsub_task
    except asyncio.CancelledError:
        pass
    await close_redis_client()
    await engine.dispose()
    logger.info("Cleanup complete.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Distributed Notification Delivery System - Asynchronous, Idempotent, Rate-limited Notification Service",
    lifespan=lifespan
)

# Enable CORS for local Vite frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Routers
app.include_router(api_v1_router, prefix="/api")
app.include_router(ws_router)


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for container orchestrators and load balancers."""
    return {"status": "ok", "service": settings.PROJECT_NAME, "version": settings.VERSION}
