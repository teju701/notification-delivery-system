import enum
import uuid
from datetime import datetime
from typing import Any, Dict
from sqlalchemy import String, Integer, DateTime, ForeignKey, Enum as SQLEnum, JSON, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel



class NotificationStatus(str, enum.Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    DELIVERED = "delivered"
    RETRYING = "retrying"
    FAILED = "failed"


class NotificationChannel(str, enum.Enum):
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"


class Notification(BaseModel):
    """
    Stores notification state and payload.
    """
    __tablename__ = "notifications"

    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    idempotency_key: Mapped[str] = mapped_column(String(255), nullable=False)
    channel: Mapped[NotificationChannel] = mapped_column(
        SQLEnum(NotificationChannel, native_enum=False),
        default=NotificationChannel.EMAIL,
        nullable=False
    )
    recipient: Mapped[str] = mapped_column(String(255), nullable=False)
    template_id: Mapped[str] = mapped_column(String(255), nullable=False)
    payload: Mapped[Dict[str, Any]] = mapped_column(JSON().with_variant(JSONB, "postgresql"), nullable=False, default=dict)
    
    status: Mapped[NotificationStatus] = mapped_column(
        SQLEnum(NotificationStatus, native_enum=False),
        default=NotificationStatus.QUEUED,
        nullable=False,
        index=True
    )

    attempt_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    max_attempts: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    tenant = relationship("Tenant", back_populates="notifications")
    delivery_attempts = relationship("DeliveryAttempt", back_populates="notification", cascade="all, delete-orphan", lazy="selectin", order_by="DeliveryAttempt.attempt_number")
