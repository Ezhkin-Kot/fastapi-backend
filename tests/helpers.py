import uuid
from datetime import datetime, timezone
from httpx import AsyncClient
from passlib.context import CryptContext

from src.db.db import database
from src.db.models import User
from src.db.repositories.users import UserRepository

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def create_user_directly(user_suffix: str, is_superuser: bool = False) -> dict:
    """
    Creates a user directly in the database.
    Returns the user data dictionary with plain password for login.
    """
    user_data = {
        "first_name": "Test",
        "last_name": "User",
        "username": f"testuser_{user_suffix}",
        "email": f"testuser_{user_suffix}@example.com",
        "password": "Password123",
    }

    user_model_data = {
        "first_name": user_data["first_name"],
        "last_name": user_data["last_name"],
        "username": user_data["username"],
        "email": user_data["email"],
        "hashed_password": pwd_context.hash(user_data["password"]),
        "is_superuser": is_superuser,
        "is_active": True,
    }

    async with database.session() as session:
        user_repo = UserRepository(session)
        await user_repo.create(user_model_data)
        await session.commit()

    return user_data


async def login_user(test_app: AsyncClient, username: str, password: str) -> str:
    """Logs in a user and returns the access token."""
    login_data = {"username": username, "password": password}
    token_response = await test_app.post("/api/v1/auth/token", data=login_data)
    assert token_response.status_code == 200, token_response.text
    token = token_response.json()["access_token"]
    return token


async def create_user_and_login(test_app: AsyncClient, user_suffix: str):
    """Creates a regular user via API, logs them in, and returns their token."""
    user_data = {
        "first_name": "Test",
        "last_name": "User",
        "username": f"testuser_{user_suffix}",
        "email": f"testuser_{user_suffix}@example.com",
        "password": "Password123",
    }
    register_response = await test_app.post("/api/v1/users/register", json=user_data)
    assert register_response.status_code == 201, register_response.text

    token = await login_user(test_app, user_data["username"], user_data["password"])
    return token, register_response.json()["id"]


async def create_category(test_app: AsyncClient, token: str, slug: str, title: str):
    """Creates a category using an admin user token."""
    headers = {"Authorization": f"Bearer {token}"}
    category_data = {"title": title, "description": "desc", "slug": slug}
    response = await test_app.post(
        "/api/v1/admin/categories/", headers=headers, json=category_data
    )
    assert response.status_code == 201, response.text
    return response.json()


async def create_post(
    test_app: AsyncClient,
    token: str,
    title: str,
    text: str = "Some text",
    category_id: str = None,
):
    """Creates a post."""
    headers = {"Authorization": f"Bearer {token}"}
    post_data = {
        "title": title,
        "text": text,
        "pub_date": datetime.now(timezone.utc).isoformat(),
        "category_id": category_id,
    }
    response = await test_app.post("/api/v1/posts/", headers=headers, json=post_data)
    assert response.status_code == 201, response.text
    return response.json()


async def create_comment(
    test_app: AsyncClient, token: str, post_id: uuid.UUID, text: str
):
    """Creates a comment on a post."""
    headers = {"Authorization": f"Bearer {token}"}
    comment_data = {"text": text}
    response = await test_app.post(
        f"/api/v1/posts/{post_id}/comments/", headers=headers, json=comment_data
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]
