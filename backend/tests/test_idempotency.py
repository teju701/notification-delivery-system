import pytest
from httpx import AsyncClient
from app.models.tenant import Tenant


@pytest.mark.asyncio
async def test_idempotency_returns_same_notification(client: AsyncClient, test_tenant: tuple[Tenant, str]):
    tenant, raw_api_key = test_tenant
    headers = {"X-API-Key": raw_api_key}

    payload = {
        "idempotency_key": "unique-order-key-999",
        "channel": "email",
        "recipient": "test@example.com",
        "template_id": "welcome_email",
        "payload": {"user_id": "usr_123"}
    }

    # First request: should create and return 202 Accepted
    res1 = await client.post("/api/v1/notifications", json=payload, headers=headers)
    assert res1.status_code == 202
    data1 = res1.json()
    notification_id_1 = data1["id"]
    assert data1["idempotency_key"] == "unique-order-key-999"
    assert data1["status"] == "queued"

    # Second request with EXACT same idempotency key: should return HTTP 200 with same notification
    res2 = await client.post("/api/v1/notifications", json=payload, headers=headers)
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["id"] == notification_id_1
    assert data2["idempotency_key"] == "unique-order-key-999"
