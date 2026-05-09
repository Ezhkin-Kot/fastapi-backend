from httpx import AsyncClient, ASGITransport
import pytest

@pytest.mark.asyncio
async def test_read_root_not_found(test_app):
    response = await test_app.get("/")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_health_check(test_app):
    response = await test_app.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
