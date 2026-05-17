import uuid
from datetime import datetime, timezone
from httpx import AsyncClient


async def create_user_and_login(
    test_app: AsyncClient, user_suffix: str, is_superuser: bool = False
):
    """Creates a user, logs them in, and returns their token and ID."""
    user_data = {
        "first_name": "Test",
        "last_name": "User",
        "username": f"testuser_{user_suffix}",
        "email": f"testuser_{user_suffix}@example.com",
        "password": "Password123",
        "is_superuser": is_superuser,
    }
    register_response = await test_app.post("/api/v1/users/register", json=user_data)
    assert register_response.status_code == 201, register_response.text
    user_id = register_response.json()["id"]

    login_data = {"username": user_data["username"], "password": user_data["password"]}
    token_response = await test_app.post("/api/v1/auth/token", data=login_data)
    assert token_response.status_code == 200, token_response.text
    token = token_response.json()["access_token"]
    return token, user_id


async def create_category(test_app: AsyncClient, token: str, slug: str, title: str):
    """Creates a category using an admin user token."""
    headers = {"Authorization": f"Bearer {token}"}
    category_data = {"title": title, "description": "desc", "slug": slug}
    response = await test_app.post(
        "/api/v1/categories/", headers=headers, json=category_data
    )
    assert response.status_code == 200, response.text
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
