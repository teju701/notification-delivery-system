import time
import json
import logging
import asyncio
import redis.asyncio as aioredis
from app.core.config import settings

logger = logging.getLogger(__name__)


async def schedule_delayed_job(
    redis: aioredis.Redis,
    notification_id: str,
    tenant_id: str,
    recipient: str,
    attempt_count: int,
    delay_seconds: float
) -> None:
    """
    Schedules a notification retry by putting it in Redis Sorted Set 'delayed_jobs'
    with score = current_unix_timestamp + delay_seconds.
    """
    ready_at = time.time() + delay_seconds
    payload = {
        "notification_id": notification_id,
        "tenant_id": tenant_id,
        "recipient": recipient,
        "attempt_count": attempt_count,
        "retry_at": ready_at
    }
    payload_str = json.dumps(payload)

    await redis.zadd(settings.DELAYED_JOBS_KEY, {payload_str: ready_at})
    logger.info(
        f"Scheduled retry for notification {notification_id} (Attempt #{attempt_count}) in {delay_seconds:.1f}s at timestamp {ready_at}"
    )


async def run_delayed_job_scheduler(redis: aioredis.Redis, poll_interval: float = 1.0) -> None:
    """
    Background worker task scanning 'delayed_jobs' zset periodically.
    Moves mature jobs (score <= current_timestamp) back into 'notifications_stream'.
    """
    logger.info(f"Starting Delayed Job Scheduler scanning '{settings.DELAYED_JOBS_KEY}' every {poll_interval}s...")
    
    while True:
        try:
            now = time.time()
            # Fetch all items with score ready <= now
            due_items = await redis.zrangebyscore(
                settings.DELAYED_JOBS_KEY,
                min=0,
                max=now
            )

            for item_str in due_items:
                # Atomically remove from zset first
                removed = await redis.zrem(settings.DELAYED_JOBS_KEY, item_str)
                if removed:
                    data = json.loads(item_str)
                    stream_payload = {
                        "notification_id": data["notification_id"],
                        "tenant_id": data["tenant_id"],
                        "recipient": data["recipient"],
                        "attempt_count": data.get("attempt_count", 0),
                        "requeued_from_backoff": "true"
                    }
                    await redis.xadd(
                        settings.NOTIFICATION_STREAM,
                        fields={"payload": json.dumps(stream_payload)}
                    )
                    logger.info(f"Requeued due job for notification {data['notification_id']} back to {settings.NOTIFICATION_STREAM}")

        except asyncio.CancelledError:
            logger.info("Delayed job scheduler loop cancelled.")
            break
        except Exception as e:
            logger.error(f"Error in delayed job scheduler loop: {str(e)}", exc_info=True)

        await asyncio.sleep(poll_interval)
