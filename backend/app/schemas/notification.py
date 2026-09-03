import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field, EmailStr
from app.models.notification import NotificationStatus, NotificationChannel


class NotificationCreateRequest(BaseModel):
    """
    Schema for POST /api/v1/notifications ingestion endpoint.
    """
    idempotency_key: str = Field(..., min_length=1, max_length=255, description="Client-supplied unique key for request deduplication")
    channel: NotificationChannel = Field(default=NotificationChannel.EMAIL, description="Channel to send delivery through")
    recipient: str = Field(..., min_length=3, max_length=255, description="Target recipient email/phone")
    template_id: str = Field(..., min_length=1, max_length=255, description="Identifier for template to render")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Dynamic payload data for template rendering")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "idempotency_key": "order-10293-shipment",
                "channel": "email",
                "recipient": "user@example.com",
                "template_id": "shipping_confirmation",
                "payload": {
                    "order_id": "10293",
                    "carrier": "FedEx",
                    "tracking_number": "1234567890"
                }
            }
        }
    )


class DeliveryAttemptResponse(BaseModel):
    id: uuid.UUID
    attempt_number: int
    status: str
    error_message: Optional[str] = None
    attempted_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NotificationResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    idempotency_key: str
    channel: NotificationChannel
    recipient: str
    template_id: str
    payload: Dict[str, Any]
    status: NotificationStatus
    attempt_count: int
    max_attempts: int
    created_at: datetime
    updated_at: datetime
    delivery_attempts: List[DeliveryAttemptResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class NotificationListResponse(BaseModel):
    total: int
    items: List[NotificationResponse]
