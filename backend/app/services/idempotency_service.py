import uuid
import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.idempotency import IdempotencyKey
from app.models.notification import Notification

logger = logging.getLogger(__name__)


class IdempotencyService:

    @staticmethod
    async def get_existing_notification(
        db: AsyncSession,
        tenant_id: uuid.UUID,
        key: str
    ) -> Notification | None:
        """
        Queries idempotency_keys table for (tenant_id, key).
        If present, fetches and returns existing notification record with delivery attempts.
        """
        stmt = (
            select(IdempotencyKey)
            .where(
                IdempotencyKey.tenant_id == tenant_id,
                IdempotencyKey.key == key
            )
        )
        result = await db.execute(stmt)
        idem_record = result.scalar_one_or_none()

        if not idem_record:
            return None

        # Fetch notification with delivery_attempts eagerly loaded
        notif_stmt = (
            select(Notification)
            .options(selectinload(Notification.delivery_attempts))
            .where(Notification.id == idem_record.notification_id)
        )
        notif_result = await db.execute(notif_stmt)
        return notif_result.scalar_one_or_none()

    @staticmethod
    async def record_key(
        db: AsyncSession,
        tenant_id: uuid.UUID,
        key: str,
        notification_id: uuid.UUID
    ) -> IdempotencyKey:
        """
        Creates an idempotency record mapping (tenant_id, key) -> notification_id.
        """
        idem_record = IdempotencyKey(
            tenant_id=tenant_id,
            key=key,
            notification_id=notification_id
        )
        db.add(idem_record)
        return idem_record
