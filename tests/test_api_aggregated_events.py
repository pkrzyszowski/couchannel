import asyncio

from fastapi.testclient import TestClient
from httpx import AsyncClient, MockTransport, Request, Response

from services.api.app.http_client import get_http_client
from services.api.app.main import app
from services.identity.app.auth import JWKS, mint_token


def test_aggregated_events_calls_inventory_and_identity() -> None:
    def handler(request: Request) -> Response:
        if request.url.path == "/events":
            return Response(
                200,
                json=[
                    {
                        "id": "event-1",
                        "title": "El Clasico",
                        "starts_at": "2025-01-01T20:00:00Z",
                        "slots_total": 5,
                        "slots_available": 3,
                        "location": "Warszawa",
                        "price_pln": 90,
                        "host_id": "host-123",
                    }
                ],
            )
        if request.url.path == "/profiles/host-123":
            return Response(
                200,
                json={
                    "user_id": "host-123",
                    "display_name": "Ania",
                    "reputation": 4.9,
                    "views": 12,
                },
            )
        if request.url.path == "/.well-known/jwks.json":
            return Response(200, json=JWKS)
        raise AssertionError(f"Unexpected path: {request.url.path}")

    transport = MockTransport(handler)
    async_client = AsyncClient(transport=transport)

    async def override_client() -> AsyncClient:
        return async_client

    app.dependency_overrides[get_http_client] = override_client

    client = TestClient(app)
    token = mint_token("demo-user")
    response = client.get(
        "/events/aggregated",
        headers={"Authorization": f"Bearer {token['access_token']}"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload[0]["host"]["display_name"] == "Ania"

    app.dependency_overrides.clear()
    asyncio.run(async_client.aclose())
