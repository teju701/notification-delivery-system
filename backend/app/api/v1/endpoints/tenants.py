import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import generate_api_key
from app.models.tenant import Tenant
from app.schemas.tenant import TenantCreate, TenantWithApiKeyResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tenants", tags=["Tenants & Auth"])


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=TenantWithApiKeyResponse,
    summary="Register a new tenant & generate API key"
)
async def register_tenant(
    req: TenantCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Public Endpoint:
    Registers a new tenant/application, generates a secure X-API-Key (prefix nds_live_),
    saves the hashed key in PostgreSQL, and returns the raw API key once to the caller.
    """
    if not req.name or len(req.name.strip()) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Application / Tenant name must be at least 2 characters long."
        )

    # Generate raw and hashed API key
    raw_key, hashed_key = generate_api_key(prefix="nds_live_")

    tenant = Tenant(
        name=req.name.strip(),
        api_key_hash=hashed_key,
        rate_limit_rps=10  # Default 10 requests per second
    )

    db.add(tenant)
    await db.commit()
    await db.refresh(tenant)

    logger.info(f"Registered new tenant '{tenant.name}' (ID: {tenant.id})")

    return TenantWithApiKeyResponse(
        id=tenant.id,
        name=tenant.name,
        rate_limit_rps=tenant.rate_limit_rps,
        created_at=tenant.created_at,
        api_key=raw_key
    )
