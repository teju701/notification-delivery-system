import json
import uuid
import time
import logging
import asyncio
import redis.asyncio as aioredis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.models.notification import Notification, NotificationStatus
from app.models.delivery_attempt import DeliveryAttempt
from app.providers import get_email_provider
from app.services.rate_limiter import RedisRateLimiter
from app.worker.scheduler import schedule_delayed_job, run_delayed_job_scheduler

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] [WORKER] [%(name)s] %(message)s"
)
logger = logging.getLogger("worker")

# Worker standalone database engine
worker_engine = create_async_engine(
    settings.async_database_url,
    pool_size=10,
    max_overflow=5
)
WorkerSessionLocal = async_sessionmaker(bind=worker_engine, class_=AsyncSession, expire_on_commit=False)


async def init_redis_consumer_group(redis: aioredis.Redis) -> None:
    """Ensures Redis Stream and Consumer Group exist."""
    try:
        await redis.xgroup_create(
            name=settings.NOTIFICATION_STREAM,
            groupname=settings.NOTIFICATION_GROUP,
            id="0",
            mkstream=True
        )
        logger.info(f"Created Redis Stream consumer group '{settings.NOTIFICATION_GROUP}'")
    except aioredis.ResponseError as e:
        if "BUSYGROUP" in str(e):
            logger.info(f"Consumer group '{settings.NOTIFICATION_GROUP}' already exists.")
        else:
            raise e


async def publish_ws_update(redis: aioredis.Redis, notification: Notification) -> None:
    """Helper to publish real-time notification state updates over Redis PubSub."""
    payload = {
        "type": "NOTIFICATION_STATUS_UPDATE",
        "notification_id": str(notification.id),
        "tenant_id": str(notification.tenant_id),
        "status": notification.status.value,
        "attempt_count": notification.attempt_count,
        "recipient": notification.recipient,
        "channel": notification.channel.value,
        "created_at": notification.created_at.isoformat(),
        "updated_at": notification.updated_at.isoformat() if notification.updated_at else notification.created_at.isoformat()
    }
    await redis.publish(settings.PUBSUB_CHANNEL, json.dumps(payload))


async def process_notification_job(
    redis: aioredis.Redis,
    rate_limiter: RedisRateLimiter,
    notification_id_str: str
) -> bool:
    """
    Core Worker Pipeline for processing a single notification job:
    1. Fetch notification from PostgreSQL.
    2. Check Global Provider Rate Limit.
    3. Transition status -> 'processing'.
    4. Invoke EmailProvider abstraction.
    5. On Success: transition status -> 'delivered', record audit log.
    6. On Failure:
       - If attempt < max_attempts -> status -> 'retrying', schedule delayed retry ($2^{attempt}$).
       - Else -> status -> 'failed', push to DLQ stream.
    """
    try:
        notif_uuid = uuid.UUID(notification_id_str)
    except ValueError:
        logger.error(f"Invalid UUID in stream job payload: {notification_id_str}")
        return True

    async with WorkerSessionLocal() as db:
        stmt = select(Notification).where(Notification.id == notif_uuid)
        res = await db.execute(stmt)
        notification = res.scalar_one_or_none()

        if not notification:
            logger.warning(f"Notification record {notif_uuid} not found in database. Skipping.")
            return True

        if notification.status in (NotificationStatus.DELIVERED, NotificationStatus.FAILED):
            logger.info(f"Notification {notif_uuid} is already in terminal state '{notification.status}'. Skipping.")
            return True

        # Check Global Email Provider Rate Limit (e.g. 5 RPS)
        provider_allowed, retry_after = await rate_limiter.is_allowed(
            identifier="provider:global",
            rate=float(settings.PROVIDER_GLOBAL_RPS),
            capacity=float(settings.PROVIDER_GLOBAL_RPS)
        )

        if not provider_allowed:
            logger.warning(f"Global email provider rate limit hit. Requeueing notification {notif_uuid} after {retry_after:.2f}s")
            await schedule_delayed_job(
                redis=redis,
                notification_id=str(notification.id),
                tenant_id=str(notification.tenant_id),
                recipient=notification.recipient,
                attempt_count=notification.attempt_count,
                delay_seconds=max(1.0, retry_after)
            )
            return True

        # Mark Processing
        notification.status = NotificationStatus.PROCESSING
        await db.commit()
        await db.refresh(notification)
        await publish_ws_update(redis, notification)
        logger.info(f"Notification {notif_uuid} transitioned to PROCESSING")

        # Execute Send via Email Provider
        provider = get_email_provider()
        subject = f"Notification ({notification.template_id})"
        content = f"Hello, you have a notification regarding template '{notification.template_id}'."
        
        result = await provider.send_email(
            recipient=notification.recipient,
            subject=subject,
            content=content,
            payload=notification.payload
        )

        # Record attempt
        next_attempt_number = notification.attempt_count + 1
        notification.attempt_count = next_attempt_number

        attempt_log = DeliveryAttempt(
            notification_id=notification.id,
            attempt_number=next_attempt_number,
            status="delivered" if result.success else "failed",
            error_message=result.error
        )
        db.add(attempt_log)

        if result.success:
            notification.status = NotificationStatus.DELIVERED
            await db.commit()
            await db.refresh(notification)
            await publish_ws_update(redis, notification)
            logger.info(f"Notification {notif_uuid} successfully DELIVERED on attempt #{next_attempt_number}")
        else:
            logger.warning(f"Delivery failed for notification {notif_uuid} on attempt #{next_attempt_number}: {result.error}")
            
            if next_attempt_number < notification.max_attempts:
                notification.status = NotificationStatus.RETRYING
                await db.commit()
                await db.refresh(notification)
                await publish_ws_update(redis, notification)

                # Exponential backoff formula: 2 ^ attempt_count seconds
                backoff_delay = float(2 ** next_attempt_number)
                await schedule_delayed_job(
                    redis=redis,
                    notification_id=str(notification.id),
                    tenant_id=str(notification.tenant_id),
                    recipient=notification.recipient,
                    attempt_count=next_attempt_number,
                    delay_seconds=backoff_delay
                )
            else:
                notification.status = NotificationStatus.FAILED
                await db.commit()
                await db.refresh(notification)
                await publish_ws_update(redis, notification)

                # Move to Dead-Letter Queue (DLQ Stream)
                dlq_payload = {
                    "notification_id": str(notification.id),
                    "tenant_id": str(notification.tenant_id),
                    "recipient": notification.recipient,
                    "final_attempt_count": next_attempt_number,
                    "last_error": result.error,
                    "failed_at": time.time()
                }
                await redis.xadd(settings.DLQ_STREAM, fields={"payload": json.dumps(dlq_payload)})
                logger.error(f"Notification {notif_uuid} permanently FAILED after {next_attempt_number} attempts. Moved to DLQ '{settings.DLQ_STREAM}'")

        return True


async def start_worker():
    """
    Worker Process Entrypoint:
    Runs stream consumer loop and delayed job scheduler loop concurrently.
    """
    logger.info("Initializing Notification Worker service...")
    redis = aioredis.from_url(settings.get_redis_url, encoding="utf-8", decode_responses=True)
    rate_limiter = RedisRateLimiter(redis)

    await init_redis_consumer_group(redis)

    # Spawn background scheduler task for delayed retries
    scheduler_task = asyncio.create_task(run_delayed_job_scheduler(redis))

    worker_id = f"worker-{uuid.uuid4().hex[:6]}"
    logger.info(f"Worker process '{worker_id}' actively polling Redis stream '{settings.NOTIFICATION_STREAM}'...")

    try:
        while True:
            try:
                # Read new jobs from Redis Stream via Consumer Group
                streams = await redis.xreadgroup(
                    groupname=settings.NOTIFICATION_GROUP,
                    consumername=worker_id,
                    streams={settings.NOTIFICATION_STREAM: ">"},
                    count=5,
                    block=2000  # 2 second block
                )

                if streams:
                    for stream_name, messages in streams:
                        for msg_id, fields in messages:
                            payload_raw = fields.get("payload", "{}")
                            try:
                                data = json.loads(payload_raw)
                                notif_id = data.get("notification_id")
                                if notif_id:
                                    await process_notification_job(redis, rate_limiter, notif_id)
                            except json.JSONDecodeError:
                                logger.error(f"Malformed stream payload: {payload_raw}")
                            
                            # Acknowledge processed message in consumer group
                            await redis.xack(settings.NOTIFICATION_STREAM, settings.NOTIFICATION_GROUP, msg_id)
            
            except aioredis.ConnectionError as ce:
                logger.error(f"Redis connection lost: {ce}. Retrying in 3 seconds...")
                await asyncio.sleep(3.0)
            except Exception as e:
                logger.error(f"Error in worker consumption loop: {str(e)}", exc_info=True)
                await asyncio.sleep(1.0)

    except asyncio.CancelledError:
        logger.info("Worker process shutting down...")
    finally:
        scheduler_task.cancel()
        await redis.aclose()
        await worker_engine.dispose()
        logger.info("Worker resources cleaned up.")


if __name__ == "__main__":
    asyncio.run(start_worker())
