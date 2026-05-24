import pytest
from httpx import AsyncClient

from src.db.db import database
from src.db.models.users import User
from src.resources.auth import get_password_hash

TEST_USER_PASSWORD = "testpassword"


@pytest.fixture
async def test_user():
    """Fixture to create a test user in the database."""
    user_data = {
        "first_name": "Test",
        "last_name": "User",
        "username": "testuser",
        "email": "test@example.com",
        "hashed_password": get_password_hash(TEST_USER_PASSWORD),
        "is_active": True,
    }
    async with database.session() as session:
        user = User(**user_data)
        session.add(user)
        await session.commit()
        await session.refresh(user)
    return user


@pytest.mark.asyncio
async def test_login_for_access_token(test_app: AsyncClient, test_user: User):
    """Test successful login and token generation."""
    response = await test_app.post(
        "/api/v1/auth/token",
        data={"username": test_user.username, "password": TEST_USER_PASSWORD},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_refresh_token(test_app: AsyncClient, test_user: User):
    """Test successful token refresh."""
    # 1. Log in to get initial tokens
    login_response = await test_app.post(
        "/api/v1/auth/token",
        data={"username": test_user.username, "password": TEST_USER_PASSWORD},
    )
    assert login_response.status_code == 200
    login_data = login_response.json()
    old_access_token = login_data["access_token"]
    old_refresh_token = login_data["refresh_token"]

    # 2. Use the refresh token to get new tokens
    refresh_response = await test_app.post(
        "/api/v1/auth/refresh", data={"refresh_token": old_refresh_token}
    )
    assert refresh_response.status_code == 200
    refresh_data = refresh_response.json()
    new_access_token = refresh_data["access_token"]
    new_refresh_token = refresh_data["refresh_token"]

    # 3. Assert new tokens are different from old ones
    assert new_access_token != old_access_token
    assert new_refresh_token != old_refresh_token


@pytest.mark.asyncio
async def test_refresh_token_rotation(test_app: AsyncClient, test_user: User):
    """Test that a used refresh token cannot be used again."""
    # 1. Log in
    login_response = await test_app.post(
        "/api/v1/auth/token",
        data={"username": test_user.username, "password": TEST_USER_PASSWORD},
    )
    old_refresh_token = login_response.json()["refresh_token"]

    # 2. Refresh once
    await test_app.post(
        "/api/v1/auth/refresh", data={"refresh_token": old_refresh_token}
    )

    # 3. Try to use the first refresh token again
    reuse_response = await test_app.post(
        "/api/v1/auth/refresh", data={"refresh_token": old_refresh_token}
    )
    assert reuse_response.status_code == 401
    assert "Invalid or expired refresh token" in reuse_response.json()["detail"]


@pytest.mark.asyncio
async def test_logout(test_app: AsyncClient, test_user: User):
    """Test that logout invalidates both access and refresh tokens."""
    # 1. Log in
    login_response = await test_app.post(
        "/api/v1/auth/token",
        data={"username": test_user.username, "password": TEST_USER_PASSWORD},
    )
    token_data = login_response.json()
    access_token = token_data["access_token"]
    refresh_token = token_data["refresh_token"]
    headers = {
        "Authorization": f"Bearer {access_token}",
        "X-Refresh-Token": refresh_token,
    }

    # 2. Verify token is valid before logout
    me_response_before = await test_app.get("/api/v1/users/me", headers=headers)
    assert me_response_before.status_code == 200

    # 3. Log out
    logout_response = await test_app.post("/api/v1/auth/logout", headers=headers)
    assert logout_response.status_code == 200
    assert logout_response.json() == {"message": "Logged out successfully"}

    # 4. Verify access token is now invalid
    me_response_after = await test_app.get("/api/v1/users/me", headers=headers)
    assert me_response_after.status_code == 401
    assert "Could not validate credentials" in me_response_after.json()["detail"]

    # 5. Verify refresh token is now invalid
    refresh_response_after = await test_app.post(
        "/api/v1/auth/refresh", data={"refresh_token": refresh_token}
    )
    assert refresh_response_after.status_code == 401
    assert "Invalid or expired refresh token" in refresh_response_after.json()["detail"]
