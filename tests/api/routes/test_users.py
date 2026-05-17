import pytest
from httpx import AsyncClient
from datetime import datetime, timezone


# Helper functions
async def create_user_and_login(test_app: AsyncClient, user_suffix: str):
    user_data = {
        "first_name": "Test",
        "last_name": "User",
        "username": f"testuser_{user_suffix}",
        "email": f"testuser_{user_suffix}@example.com",
        "password": "Password123",
    }
    register_response = await test_app.post("/api/v1/users/register", json=user_data)
    assert register_response.status_code == 201
    user_id = register_response.json()["id"]
    login_data = {"username": user_data["username"], "password": user_data["password"]}
    token_response = await test_app.post("/api/v1/auth/token", data=login_data)
    assert token_response.status_code == 200
    token = token_response.json()["access_token"]
    return token, user_id


async def create_post(test_app: AsyncClient, token: str, title: str):
    headers = {"Authorization": f"Bearer {token}"}
    post_data = {
        "title": title,
        "text": "Some text",
        "pub_date": datetime.now(timezone.utc).isoformat(),
    }
    create_post_response = await test_app.post(
        "/api/v1/posts/", headers=headers, json=post_data
    )
    assert create_post_response.status_code == 201
    return create_post_response.json()


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
    assert "posts" in response_data
    assert response_data["posts"] == []


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
    assert "posts" in response_data


@pytest.mark.asyncio
async def test_get_users(test_app: AsyncClient):
    token, _ = await create_user_and_login(test_app, "get_all1")
    await create_user_and_login(test_app, "get_all2")
    headers = {"Authorization": f"Bearer {token}"}
    response = await test_app.get("/api/v1/users/", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) >= 2


# Renamed test for clarity
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


# Renamed test for clarity
@pytest.mark.asyncio
async def test_delete_own_user(test_app: AsyncClient):
    token, user_id = await create_user_and_login(test_app, "delete_own")
    headers = {"Authorization": f"Bearer {token}"}
    response = await test_app.delete(f"/api/v1/users/{user_id}", headers=headers)
    assert response.status_code == 204
    # Verify user is gone (should get 401 on protected endpoint)
    response = await test_app.get("/api/v1/users/me", headers=headers)
    assert response.status_code == 401


# --- New Tests ---


@pytest.mark.asyncio
async def test_get_user_with_posts(test_app: AsyncClient):
    token, user_id = await create_user_and_login(test_app, "get_with_posts")
    post1 = await create_post(test_app, token, "First Post")
    post2 = await create_post(test_app, token, "Second Post")

    headers = {"Authorization": f"Bearer {token}"}
    response = await test_app.get(f"/api/v1/users/{user_id}", headers=headers)
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["id"] == user_id
    assert "posts" in response_data
    assert len(response_data["posts"]) == 2
    post_titles = {p["title"] for p in response_data["posts"]}
    assert post1["title"] in post_titles
    assert post2["title"] in post_titles


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
