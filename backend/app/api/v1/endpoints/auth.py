import logging
from fastapi import Header, HTTPException, Security, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import hash_api_key
from app.models.tenant import Tenant

logger = logging.getLogger(__name__)


async def get_current_tenant(
    x_api_key: str = Header(..., alias="X-API-Key", description="Tenant API Secret Key"),
    db: AsyncSession = Depends(get_db)
) -> Tenant:
    """
    FastAPI dependency validating the X-API-Key header against the hashed tenant keys in Postgres.
    """
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-API-Key header"
        )

    hashed_key = hash_api_key(x_api_key)
    stmt = select(Tenant).where(Tenant.api_key_hash == hashed_key)
    result = await db.execute(stmt)
    tenant = result.scalar_one_or_none()

    if not tenant:
        logger.warning("Authentication failed: invalid X-API-Key provided")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key"
        )

    return tenant
