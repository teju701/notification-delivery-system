import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_new_tenant(client: AsyncClient):
    """
    Test registering a new tenant generates a valid API key,
    persists in PostgreSQL, and allows authenticating subsequent notification calls.
    """
    reg_payload = {"name": "Test Acme Billing Service"}
    response = await client.post("/api/v1/tenants/register", json=reg_payload)

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Acme Billing Service"
    assert "api_key" in data
    assert data["api_key"].startswith("nds_live_")

    # Use newly generated raw API key to send a notification
    new_api_key = data["api_key"]
    headers = {"X-API-Key": new_api_key}
    notif_payload = {
        "idempotency_key": "acme-test-123",
        "channel": "email",
        "recipient": "acme@example.com",
        "template_id": "receipt_template",
        "payload": {"amount": 99.99}
    }

    notif_response = await client.post("/api/v1/notifications", json=notif_payload, headers=headers)
    assert notif_response.status_code == 202
    notif_data = notif_response.json()
    assert notif_data["recipient"] == "acme@example.com"
