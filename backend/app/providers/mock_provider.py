import uuid
import logging
import asyncio
from typing import Any, Dict
from app.providers.base import EmailProvider, EmailDeliveryResult

logger = logging.getLogger(__name__)


class ConsoleMockEmailProvider(EmailProvider):
    """
    Mock Email Provider that logs email sends to console.
    Can simulate failure if recipient contains 'fail' or payload specifies simulate_fail=True.
    """

    async def send_email(
        self,
        recipient: str,
        subject: str,
        content: str,
        payload: Dict[str, Any]
    ) -> EmailDeliveryResult:
        # Simulate small network latency (50-150ms)
        await asyncio.sleep(0.1)

        # Check for forced failure simulation
        if "fail" in recipient.lower() or payload.get("simulate_fail") is True:
            logger.warning(f"[MOCK EMAIL PROVIDER] Simulated failure for recipient {recipient}")
            return EmailDeliveryResult(
                success=False,
                error="Provider 503 Service Unavailable: Simulated downstream network timeout"
            )

        msg_id = f"mock-msg-{uuid.uuid4().hex[:12]}"
        logger.info(f"[MOCK EMAIL PROVIDER] Successfully delivered email to {recipient} (Message ID: {msg_id})")
        return EmailDeliveryResult(success=True, message_id=msg_id)
