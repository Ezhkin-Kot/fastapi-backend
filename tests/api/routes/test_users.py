from httpx import AsyncClient, ASGITransport
import pytest


@pytest.mark.asyncio
async def test_register_user(test_app):
    user_data = {
        "first_name": "Test",
        "last_name": "User",
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "Password123"
    }
    response = await test_app.post("/api/v1/users/register", json=user_data)
    assert response.status_code == 201
    response_data = response.json()
    assert response_data["email"] == user_data["email"]
    assert response_data["username"] == user_data["username"]
    assert "id" in response_data


@pytest.mark.asyncio
async def test_read_users_me(test_app):
    user_data = {
        "first_name": "Test",
        "last_name": "User",
        "username": "testuser_me",
        "email": "testuser_me@example.com",
        "password": "Password123"
    }
    # Register user
    register_response = await test_app.post("/api/v1/users/register", json=user_data)
    assert register_response.status_code == 201

    # Login to get token
    login_data = {
        "username": user_data["username"],
        "password": user_data["password"]
    }
    response = await test_app.post("/api/v1/auth/token", data=login_data)
    assert response.status_code == 200
    token = response.json()["access_token"]

    # Get current user
    headers = {"Authorization": f"Bearer {token}"}
    response = await test_app.get("/api/v1/users/me", headers=headers)
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["email"] == user_data["email"]
    assert response_data["username"] == user_data["username"]

@pytest.mark.asyncio
async def test_get_user(test_app):
    user_data = {
        "first_name": "Test",
        "last_name": "User",
        "username": "testuser_get",
        "email": "testuser_get@example.com",
        "password": "Password123"
    }
    # Register user
    register_response = await test_app.post("/api/v1/users/register", json=user_data)
    assert register_response.status_code == 201
    user_id = register_response.json()["id"]

    # Login to get token
    login_data = {
        "username": user_data["username"],
        "password": user_data["password"]
    }
    response = await test_app.post("/api/v1/auth/token", data=login_data)
    assert response.status_code == 200
    token = response.json()["access_token"]

    # Get user
    headers = {"Authorization": f"Bearer {token}"}
    response = await test_app.get(f"/api/v1/users/{user_id}", headers=headers)
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["email"] == user_data["email"]
    assert response_data["username"] == user_data["username"]
    assert response_data["id"] == user_id


@pytest.mark.asyncio
async def test_get_users(test_app):
    user1_data = {
        "first_name": "Test",
        "last_name": "User1",
        "username": "testuser1_get_all",
        "email": "testuser1_get_all@example.com",
        "password": "Password123"
    }
    user2_data = {
        "first_name": "Test",
        "last_name": "User2",
        "username": "testuser2_get_all",
        "email": "testuser2_get_all@example.com",
        "password": "Password123"
    }
    # Register users
    await test_app.post("/api/v1/users/register", json=user1_data)
    await test_app.post("/api/v1/users/register", json=user2_data)

    # Login to get token
    login_data = {
        "username": user1_data["username"],
        "password": user1_data["password"]
    }
    response = await test_app.post("/api/v1/auth/token", data=login_data)
    assert response.status_code == 200
    token = response.json()["access_token"]

    # Get all users
    headers = {"Authorization": f"Bearer {token}"}
    response = await test_app.get("/api/v1/users/", headers=headers)
    assert response.status_code == 200
    response_data = response.json()
    assert len(response_data) >= 2
    usernames = [user["username"] for user in response_data]
    assert user1_data["username"] in usernames
    assert user2_data["username"] in usernames


@pytest.mark.asyncio
async def test_update_user(test_app):
    user_data = {
        "first_name": "Test",
        "last_name": "User",
        "username": "testuser_update",
        "email": "testuser_update@example.com",
        "password": "Password123"
    }
    # Register user
    register_response = await test_app.post("/api/v1/users/register", json=user_data)
    assert register_response.status_code == 201
    user_id = register_response.json()["id"]

    # Login to get token
    login_data = {
        "username": user_data["username"],
        "password": user_data["password"]
    }
    response = await test_app.post("/api/v1/auth/token", data=login_data)
    assert response.status_code == 200
    token = response.json()["access_token"]

    # Update user
    headers = {"Authorization": f"Bearer {token}"}
    update_data = {"first_name": "Updated"}
    response = await test_app.put(f"/api/v1/users/{user_id}", headers=headers, json=update_data)
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["first_name"] == "Updated"

    # Verify update
    response = await test_app.get(f"/api/v1/users/{user_id}", headers=headers)
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["first_name"] == "Updated"


@pytest.mark.asyncio
async def test_delete_user(test_app):
    user_data = {
        "first_name": "Test",
        "last_name": "User",
        "username": "testuser_delete",
        "email": "testuser_delete@example.com",
        "password": "Password123"
    }
    # Register user
    register_response = await test_app.post("/api/v1/users/register", json=user_data)
    assert register_response.status_code == 201
    user_id = register_response.json()["id"]

    # Login to get token
    login_data = {
        "username": user_data["username"],
        "password": user_data["password"]
    }
    response = await test_app.post("/api/v1/auth/token", data=login_data)
    assert response.status_code == 200
    token = response.json()["access_token"]

    # Delete user
    headers = {"Authorization": f"Bearer {token}"}
    response = await test_app.delete(f"/api/v1/users/{user_id}", headers=headers)
    assert response.status_code == 204

    # Verify delete
    response = await test_app.get(f"/api/v1/users/{user_id}", headers=headers)
    assert response.status_code == 401

