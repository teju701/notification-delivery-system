import logging
from typing import Any, Dict
import resend
from app.core.config import settings
from app.providers.base import EmailProvider, EmailDeliveryResult

logger = logging.getLogger(__name__)


class ResendEmailProvider(EmailProvider):
    """
    Real Email Provider implementation utilizing Resend API.
    """

    def __init__(self, api_key: str | None = None, default_from: str | None = None):
        self.api_key = api_key or settings.RESEND_API_KEY
        self.default_from = default_from or settings.DEFAULT_FROM_EMAIL
        resend.api_key = self.api_key

    async def send_email(
        self,
        recipient: str,
        subject: str,
        content: str,
        payload: Dict[str, Any]
    ) -> EmailDeliveryResult:
        try:
            # Resend python SDK synchronous call wrapped in async execution context if needed
            params = {
                "from": self.default_from,
                "to": [recipient],
                "subject": subject,
                "html": f"<p>{content}</p><pre>{payload}</pre>"
            }
            logger.info(f"Sending email via Resend to {recipient}")
            r = resend.Emails.send(params)
            
            if hasattr(r, "id") and r.id:
                return EmailDeliveryResult(success=True, message_id=str(r.id))
            elif isinstance(r, dict) and "id" in r:
                return EmailDeliveryResult(success=True, message_id=str(r["id"]))
            else:
                return EmailDeliveryResult(success=False, error=f"Resend API unexpected response: {r}")
        except Exception as e:
            logger.error(f"Resend email dispatch error: {str(e)}", exc_info=True)
            return EmailDeliveryResult(success=False, error=str(e))
