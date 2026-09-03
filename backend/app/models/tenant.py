import uuid
from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel


class Tenant(BaseModel):
    """
    Represents an application client / tenant that consumes notification services.
    """
    __tablename__ = "tenants"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    api_key_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    rate_limit_rps: Mapped[int] = mapped_column(Integer, default=10, nullable=False)

    notifications = relationship("Notification", back_populates="tenant", cascade="all, delete-orphan")
    idempotency_keys = relationship("IdempotencyKey", back_populates="tenant", cascade="all, delete-orphan")
