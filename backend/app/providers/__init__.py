from app.core.config import settings
from app.providers.base import EmailProvider, EmailDeliveryResult
from app.providers.resend_provider import ResendEmailProvider
from app.providers.mock_provider import ConsoleMockEmailProvider


def get_email_provider() -> EmailProvider:
    """
    Factory function returning the configured EmailProvider.
    Uses ConsoleMockEmailProvider if ENABLE_MOCK_EMAIL is True or key is missing.
    """
    if settings.ENABLE_MOCK_EMAIL or not settings.RESEND_API_KEY or settings.RESEND_API_KEY == "mock_key":
        return ConsoleMockEmailProvider()
    return ResendEmailProvider()


__all__ = [
    "EmailProvider",
    "EmailDeliveryResult",
    "ResendEmailProvider",
    "ConsoleMockEmailProvider",
    "get_email_provider",
]
