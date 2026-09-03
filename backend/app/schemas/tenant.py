import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class TenantCreate(BaseModel):
    name: str


class TenantResponse(BaseModel):
    id: uuid.UUID
    name: str
    rate_limit_rps: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TenantWithApiKeyResponse(TenantResponse):
    api_key: str
