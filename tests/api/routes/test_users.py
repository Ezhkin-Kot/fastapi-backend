import pytest
from httpx import AsyncClient
from tests.helpers import create_user_and_login, create_post


# Existing tests with minor modifications
@pytest.mark.asyncio
async def test_register_user(test_app: AsyncClient):
    user_data = {
        "first_name": "Test",
        "last_name": "User",
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "Password123",
    }
    response = await test_app.post("/api/v1/users/register", json=user_data)
    assert response.status_code == 201
    response_data = response.json()
    assert response_data["email"] == user_data["email"]
    assert response_data["username"] == user_data["username"]
    assert "id" in response_data


@pytest.mark.asyncio
async def test_read_users_me(test_app: AsyncClient):
    token, user_id = await create_user_and_login(test_app, "me")
    headers = {"Authorization": f"Bearer {token}"}
    response = await test_app.get("/api/v1/users/me", headers=headers)
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["id"] == user_id


@pytest.mark.asyncio
async def test_get_user(test_app: AsyncClient):
    token, user_id = await create_user_and_login(test_app, "get_user")
    headers = {"Authorization": f"Bearer {token}"}
    response = await test_app.get(f"/api/v1/users/{user_id}", headers=headers)
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["id"] == user_id


@pytest.mark.asyncio
async def test_get_users(test_app: AsyncClient):
    token, _ = await create_user_and_login(test_app, "get_all1")
    await create_user_and_login(test_app, "get_all2")
    headers = {"Authorization": f"Bearer {token}"}
    response = await test_app.get("/api/v1/users/", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) >= 2


@pytest.mark.asyncio
async def test_update_own_user(test_app: AsyncClient):
    token, user_id = await create_user_and_login(test_app, "update_own")
    headers = {"Authorization": f"Bearer {token}"}
    update_data = {"first_name": "Updated"}
    response = await test_app.put(
        f"/api/v1/users/{user_id}", headers=headers, json=update_data
    )
    assert response.status_code == 200
    assert response.json()["first_name"] == "Updated"


@pytest.mark.asyncio
async def test_delete_own_user(test_app: AsyncClient):
    token, user_id = await create_user_and_login(test_app, "delete_own")
    headers = {"Authorization": f"Bearer {token}"}
    response = await test_app.delete(f"/api/v1/users/{user_id}", headers=headers)
    assert response.status_code == 204
    # Verify user is gone (should get 401 on protected endpoint)
    response = await test_app.get("/api/v1/users/me", headers=headers)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_other_user_fails(test_app: AsyncClient):
    _, user1_id = await create_user_and_login(test_app, "update_other1")
    token2, _ = await create_user_and_login(test_app, "update_other2")

    headers2 = {"Authorization": f"Bearer {token2}"}
    update_data = {"first_name": "UpdatedByOther"}
    response = await test_app.put(
        f"/api/v1/users/{user1_id}", headers=headers2, json=update_data
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_delete_other_user_fails(test_app: AsyncClient):
    _, user1_id = await create_user_and_login(test_app, "delete_other1")
    token2, _ = await create_user_and_login(test_app, "delete_other2")

    headers2 = {"Authorization": f"Bearer {token2}"}
    response = await test_app.delete(f"/api/v1/users/{user1_id}", headers=headers2)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_register_user_cannot_become_superuser(test_app: AsyncClient):
    user_data = {
        "first_name": "Tricky",
        "last_name": "User",
        "username": "trickyuser",
        "email": "trickyuser@example.com",
        "password": "Password123",
        "is_superuser": True,  # Attempt to become a superuser
    }
    response = await test_app.post("/api/v1/users/register", json=user_data)
    assert response.status_code == 201
    response_data = response.json()
    assert response_data["username"] == "trickyuser"
    assert response_data["is_superuser"] is False


@pytest.mark.asyncio
async def test_get_user_posts_paginated(test_app: AsyncClient):
    token, user_id = await create_user_and_login(test_app, "user_with_posts")
    headers = {"Authorization": f"Bearer {token}"}

    # Create 3 posts for the user
    for i in range(3):
        await create_post(test_app, token, f"Post {i+1}")

    # Test fetching all posts
    response = await test_app.get(f"/api/v1/users/{user_id}/posts", headers=headers)
    assert response.status_code == 200
    paginated_response = response.json()
    assert paginated_response["total"] == 3
    assert len(paginated_response["results"]) == 3
    assert {p["title"] for p in paginated_response["results"]} == {
        "Post 1",
        "Post 2",
        "Post 3",
    }

    # Test pagination size
    response = await test_app.get(
        f"/api/v1/users/{user_id}/posts?page=1&size=2", headers=headers
    )
    assert response.status_code == 200
    paginated_response = response.json()
    assert paginated_response["total"] == 3
    assert len(paginated_response["results"]) == 2

    # Test pagination page
    response = await test_app.get(
        f"/api/v1/users/{user_id}/posts?page=2&size=2", headers=headers
    )
    assert response.status_code == 200
    paginated_response = response.json()
    assert paginated_response["total"] == 3
    assert len(paginated_response["results"]) == 1
