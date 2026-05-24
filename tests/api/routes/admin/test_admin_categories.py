import pytest
from httpx import AsyncClient

from tests.helpers import create_user_directly, login_user, create_user_and_login


@pytest.mark.asyncio
async def test_category_crud(test_app: AsyncClient):
    # Create a regular user who should not have access
    user_token, _ = await create_user_and_login(test_app, "cat_user")
    headers_user = {"Authorization": f"Bearer {user_token}"}

    # Create an admin user directly in the DB
    admin_data = await create_user_directly("cat_admin", is_superuser=True)
    admin_token_data = await login_user(
        test_app, admin_data["username"], admin_data["password"]
    )
    admin_access_token = admin_token_data["access_token"]
    headers_admin = {"Authorization": f"Bearer {admin_access_token}"}

    category_data = {
        "title": "Admin Test Category",
        "description": "desc",
        "slug": "admin-test-cat",
    }

    # Non-admin fails to create
    response = await test_app.post(
        "/api/v1/admin/categories/", headers=headers_user, json=category_data
    )
    assert response.status_code == 403

    # Admin creates successfully
    response = await test_app.post(
        "/api/v1/admin/categories/", headers=headers_admin, json=category_data
    )
    assert response.status_code == 201
    category = response.json()
    category_id = category["id"]

    # Non-admin fails to update
    response = await test_app.put(
        f"/api/v1/admin/categories/{category_id}",
        headers=headers_user,
        json={"title": "New Title"},
    )
    assert response.status_code == 403

    # Admin updates successfully
    response = await test_app.put(
        f"/api/v1/admin/categories/{category_id}",
        headers=headers_admin,
        json={"title": "New Title"},
    )
    assert response.status_code == 200
    assert response.json()["title"] == "New Title"

    # Non-admin fails to delete
    response = await test_app.delete(
        f"/api/v1/admin/categories/{category_id}", headers=headers_user
    )
    assert response.status_code == 403

    # Admin deletes successfully
    response = await test_app.delete(
        f"/api/v1/admin/categories/{category_id}", headers=headers_admin
    )
    assert response.status_code == 204

    # Verify deletion
    response = await test_app.get(f"/api/v1/categories/{category_id}")
    assert response.status_code == 404
