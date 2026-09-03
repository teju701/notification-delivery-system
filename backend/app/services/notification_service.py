import json
import uuid
import logging
from typing import List, Tuple, Optional
import redis.asyncio as aioredis
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.core.config import settings
from app.models.notification import Notification, NotificationStatus
from app.models.tenant import Tenant
from app.schemas.notification import NotificationCreateRequest
from app.services.idempotency_service import IdempotencyService

logger = logging.getLogger(__name__)


class NotificationService:

    @staticmethod
    async def create_and_enqueue(
        db: AsyncSession,
        redis: aioredis.Redis,
        tenant: Tenant,
        req: NotificationCreateRequest
    ) -> Notification:
        """
        1. Insert Notification with status='queued'
        2. Insert IdempotencyKey mapping
        3. Enqueue notification_id onto Redis Stream ('notifications_stream')
        4. Publish status event onto Redis Pub/Sub
        """
        notification = Notification(
            tenant_id=tenant.id,
            idempotency_key=req.idempotency_key,
            channel=req.channel,
            recipient=req.recipient,
            template_id=req.template_id,
            payload=req.payload,
            status=NotificationStatus.QUEUED,
            attempt_count=0,
            max_attempts=3
        )
        db.add(notification)
        await db.flush()  # Populates notification.id

        # Record idempotency key
        await IdempotencyService.record_key(
            db=db,
            tenant_id=tenant.id,
            key=req.idempotency_key,
            notification_id=notification.id
        )

        await db.commit()
        await db.refresh(notification)
        notification.delivery_attempts = []

        # Push to Redis Stream
        event_payload = {
            "notification_id": str(notification.id),
            "tenant_id": str(tenant.id),
            "recipient": notification.recipient,
            "status": notification.status.value,
            "timestamp": notification.created_at.isoformat()
        }
        
        await redis.xadd(
            name=settings.NOTIFICATION_STREAM,
            fields={"payload": json.dumps(event_payload)}
        )
        logger.info(f"Enqueued notification {notification.id} onto Redis stream {settings.NOTIFICATION_STREAM}")

        # Publish WebSocket event
        await redis.publish(
            settings.PUBSUB_CHANNEL,
            json.dumps({
                "type": "NOTIFICATION_STATUS_UPDATE",
                "notification_id": str(notification.id),
                "tenant_id": str(tenant.id),
                "status": notification.status.value,
                "attempt_count": notification.attempt_count,
                "recipient": notification.recipient,
                "channel": notification.channel.value,
                "created_at": notification.created_at.isoformat(),
                "updated_at": notification.updated_at.isoformat()
            })
        )

        return notification

    @staticmethod
    async def get_by_id(
        db: AsyncSession,
        notification_id: uuid.UUID,
        tenant_id: Optional[uuid.UUID] = None
    ) -> Notification | None:
        """Fetch notification by ID with delivery attempts loaded."""
        stmt = (
            select(Notification)
            .options(selectinload(Notification.delivery_attempts))
            .where(Notification.id == notification_id)
        )
        if tenant_id:
            stmt = stmt.where(Notification.tenant_id == tenant_id)

        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def list_notifications(
        db: AsyncSession,
        tenant_id: uuid.UUID,
        status: Optional[NotificationStatus] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Tuple[List[Notification], int]:
        """Fetch paginated notification records for a tenant."""
        base_query = select(Notification).where(Notification.tenant_id == tenant_id)
        if status:
            base_query = base_query.where(Notification.status == status)

        # Count total
        count_stmt = select(func.count()).select_from(base_query.subquery())
        total_result = await db.execute(count_stmt)
        total = total_result.scalar_one()

        # Fetch page
        query = (
            base_query
            .options(selectinload(Notification.delivery_attempts))
            .order_by(desc(Notification.created_at))
            .offset(offset)
            .limit(limit)
        )
        result = await db.execute(query)
        notifications = list(result.scalars().all())

        return notifications, total
