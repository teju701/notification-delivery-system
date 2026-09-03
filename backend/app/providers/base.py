from abc import ABC, abstractmethod
from typing import Any, Dict


class EmailDeliveryResult:
    def __init__(self, success: bool, message_id: str | None = None, error: str | None = None):
        self.success = success
        self.message_id = message_id
        self.error = error

    def __repr__(self) -> str:
        return f"<EmailDeliveryResult success={self.success} message_id={self.message_id} error={self.error}>"


class EmailProvider(ABC):
    """
    Abstract Interface for Email Providers.
    Allows seamlessly swapping Resend, SendGrid, AWS SES, or a local Mock Provider.
    """

    @abstractmethod
    async def send_email(
        self,
        recipient: str,
        subject: str,
        content: str,
        payload: Dict[str, Any]
    ) -> EmailDeliveryResult:
        """
        Sends an email asynchronously and returns an EmailDeliveryResult.
        """
        pass
