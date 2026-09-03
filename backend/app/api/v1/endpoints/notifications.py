import uuid
import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Response, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as aioredis

from app.core.database import get_db
from app.core.redis import get_redis
from app.models.tenant import Tenant
from app.models.notification import NotificationStatus
from app.schemas.notification import (
    NotificationCreateRequest,
    NotificationResponse,
    NotificationListResponse,
)
from app.api.v1.endpoints.auth import get_current_tenant
from app.services.idempotency_service import IdempotencyService
from app.services.notification_service import NotificationService
from app.services.rate_limiter import RedisRateLimiter

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.post(
    "",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=NotificationResponse,
    summary="Ingest a new notification request"
)
async def create_notification(
    req: NotificationCreateRequest,
    response: Response,
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
    redis: aioredis.Redis = Depends(get_redis)
):
    """
    Ingestion Endpoint for Notifications:
    1. Idempotency Check: Returns HTTP 200 with existing payload if key already processed.
    2. Tenant Token Bucket Rate Limiting: Returns HTTP 429 with Retry-After header if exhausted.
    3. Persists notification record and enqueues job onto Redis Stream.
    """
    # 1. Idempotency Check
    existing_notification = await IdempotencyService.get_existing_notification(
        db=db,
        tenant_id=tenant.id,
        key=req.idempotency_key
    )
    if existing_notification:
        logger.info(f"Idempotent hit for tenant {tenant.id} with key '{req.idempotency_key}'. Returning existing notification {existing_notification.id}")
        response.status_code = status.HTTP_200_OK
        return existing_notification

    # 2. Rate Limiting Check (Token Bucket per tenant)
    rate_limiter = RedisRateLimiter(redis)
    tenant_rate_key = f"tenant:{tenant.id}"
    allowed, retry_after = await rate_limiter.is_allowed(
        identifier=tenant_rate_key,
        rate=float(tenant.rate_limit_rps),
        capacity=float(tenant.rate_limit_rps)
    )

    if not allowed:
        logger.warning(f"Rate limit exceeded for tenant {tenant.id}. Retry after {retry_after:.2f}s")
        response.headers["Retry-After"] = str(int(max(1, retry_after)))
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded for tenant. Please retry after {retry_after:.2f} seconds.",
            headers={"Retry-After": str(int(max(1, retry_after)))}
        )

    # 3. Create & Enqueue Notification
    notification = await NotificationService.create_and_enqueue(
        db=db,
        redis=redis,
        tenant=tenant,
        req=req
    )

    return notification


@router.get(
    "/{notification_id}",
    response_model=NotificationResponse,
    summary="Get notification status and delivery attempt history"
)
async def get_notification_status(
    notification_id: uuid.UUID,
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db)
):
    """
    Fetch a notification's current status and full audit trail of delivery attempts.
    """
    notification = await NotificationService.get_by_id(
        db=db,
        notification_id=notification_id,
        tenant_id=tenant.id
    )
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Notification with ID {notification_id} not found"
        )
    return notification


@router.get(
    "",
    response_model=NotificationListResponse,
    summary="List all notifications for tenant"
)
async def list_tenant_notifications(
    status_filter: Optional[NotificationStatus] = Query(None, alias="status"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db)
):
    """
    Paginated list of notifications for the current tenant.
    """
    items, total = await NotificationService.list_notifications(
        db=db,
        tenant_id=tenant.id,
        status=status_filter,
        limit=limit,
        offset=offset
    )
    return NotificationListResponse(total=total, items=items)
