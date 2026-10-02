import asyncio
import logging
import asyncpg
from sqlalchemy import select
from app.core.config import settings
from app.core.database import engine, AsyncSessionLocal, Base
from app.core.security import generate_api_key, hash_api_key
from app.models.tenant import Tenant

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


async def ensure_database_exists():
    """
    Ensures that the target database ('notification_db') exists in PostgreSQL.
    If it does not exist, connects to default 'postgres' database and creates it.
    """
    try:
        # Try connecting to the default database to check/create target database
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


async def seed_demo_tenant():
    """
    Creates tables if missing and seeds a demo tenant with a generated API key.
    Prints the raw API Key to console for testing.
    """
    await ensure_database_exists()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        # Check if Demo Tenant exists
        stmt = select(Tenant).where(Tenant.name == "Demo Tenant")
        result = await db.execute(stmt)
        existing_tenant = result.scalar_one_or_none()

        if existing_tenant:
            logger.info("Demo Tenant already exists in database.")
            # Generate a new API Key for testing
            raw_key, key_hash = generate_api_key(prefix="nds_demo_")
            existing_tenant.api_key_hash = key_hash
            await db.commit()
            print("\n" + "=" * 60)
            print(" DEMO TENANT UPDATED SUCCESSFULLY")
            print(f" Tenant ID:       {existing_tenant.id}")
            print(f" Tenant Name:     {existing_tenant.name}")
            print(f" Tenant RPS:      {existing_tenant.rate_limit_rps}")
            print(f" X-API-Key:       {raw_key}")
            print("=" * 60 + "\n")
            return

        # Create new Demo Tenant
        raw_key, key_hash = generate_api_key(prefix="nds_demo_")
        demo_tenant = Tenant(
            name="Demo Tenant",
            api_key_hash=key_hash,
            rate_limit_rps=10
        )
        db.add(demo_tenant)
        await db.commit()
        await db.refresh(demo_tenant)

        print("\n" + "=" * 60)
        print(" DEMO TENANT SEEDED SUCCESSFULLY")
        print(f" Tenant ID:       {demo_tenant.id}")
        print(f" Tenant Name:     {demo_tenant.name}")
        print(f" Tenant RPS:      {demo_tenant.rate_limit_rps}")
        print(f" X-API-Key:       {raw_key}")
        print(" Use this X-API-Key in your HTTP requests / React Dashboard!")
        print("=" * 60 + "\n")


if __name__ == "__main__":
    asyncio.run(seed_demo_tenant())
