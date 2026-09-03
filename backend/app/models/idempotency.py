import uuid
from datetime import datetime
from sqlalchemy import String, ForeignKey, UniqueConstraint, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel


class IdempotencyKey(BaseModel):
    """
    Enforces atomic uniqueness of (tenant_id, key) combinations.
    Maps an incoming client-provided idempotency_key to a created notification_id.
    """
    __tablename__ = "idempotency_keys"
    __table_args__ = (
        UniqueConstraint("tenant_id", "key", name="uix_tenant_idempotency_key"),
    )

    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    key: Mapped[str] = mapped_column(String(255), nullable=False)
    notification_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("notifications.id", ondelete="CASCADE"), nullable=False)

    tenant = relationship("Tenant", back_populates="idempotency_keys")
    notification = relationship("Notification")
