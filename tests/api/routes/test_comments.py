import uuid
import pytest
from httpx import AsyncClient
from datetime import datetime, timezone


# Helper function to create a user and log in, returning the token and user ID
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


# Helper function to create a post
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
    return create_post_response.json()["id"]


# Helper function to create a comment
async def create_comment(
    test_app: AsyncClient, token: str, post_id: uuid.UUID, text: str
):
    headers = {"Authorization": f"Bearer {token}"}
    comment_data = {"text": text}
    response = await test_app.post(
        f"/api/v1/posts/{post_id}/comments/", headers=headers, json=comment_data
    )
    assert response.status_code == 201
    return response.json()["id"]


@pytest.mark.asyncio
async def test_create_and_get_comments(test_app: AsyncClient):
    token, _ = await create_user_and_login(test_app, "comments_user")
    post_id = await create_post(test_app, token, "Post for Comments")

    # Create comments
    await create_comment(test_app, token, post_id, "First comment")
    await create_comment(test_app, token, post_id, "Second comment")

    # Get all comments for the post
    response = await test_app.get(f"/api/v1/posts/{post_id}/comments/")
    assert response.status_code == 200
    response_data = response.json()
    assert len(response_data) == 2
    assert {c["text"] for c in response_data} == {"First comment", "Second comment"}


@pytest.mark.asyncio
async def test_update_comment_author(test_app: AsyncClient):
    token, _ = await create_user_and_login(test_app, "update_author")
    post_id = await create_post(test_app, token, "Post for comment update")
    comment_id = await create_comment(test_app, token, post_id, "Original comment")

    # Update the comment
    headers = {"Authorization": f"Bearer {token}"}
    update_data = {"text": "This is an updated comment."}
    response = await test_app.put(
        f"/api/v1/comments/{comment_id}", headers=headers, json=update_data
    )
    assert response.status_code == 200
    assert response.json()["text"] == "This is an updated comment."


@pytest.mark.asyncio
async def test_update_comment_not_author(test_app: AsyncClient):
    token1, _ = await create_user_and_login(test_app, "update_not_author1")
    post_id = await create_post(test_app, token1, "Post for comment update fail")
    comment_id = await create_comment(test_app, token1, post_id, "User 1 comment")

    token2, _ = await create_user_and_login(test_app, "update_not_author2")

    headers2 = {"Authorization": f"Bearer {token2}"}
    update_data = {"text": "This should fail."}
    response = await test_app.put(
        f"/api/v1/comments/{comment_id}", headers=headers2, json=update_data
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_delete_comment_author(test_app: AsyncClient):
    token, _ = await create_user_and_login(test_app, "delete_author")
    post_id = await create_post(test_app, token, "Post for comment delete")
    comment_id = await create_comment(test_app, token, post_id, "Comment to delete")

    headers = {"Authorization": f"Bearer {token}"}
    response = await test_app.delete(f"/api/v1/comments/{comment_id}", headers=headers)
    assert response.status_code == 204

    # Verify it's gone
    update_data = {"text": "This should fail."}
    response_after_delete = await test_app.put(
        f"/api/v1/comments/{comment_id}", headers=headers, json=update_data
    )
    assert response_after_delete.status_code == 404


@pytest.mark.asyncio
async def test_delete_comment_not_author(test_app: AsyncClient):
    token1, _ = await create_user_and_login(test_app, "delete_not_author1")
    post_id = await create_post(test_app, token1, "Post for comment delete fail")
    comment_id = await create_comment(test_app, token1, post_id, "User 1 comment")

    token2, _ = await create_user_and_login(test_app, "delete_not_author2")

    headers2 = {"Authorization": f"Bearer {token2}"}
    response = await test_app.delete(f"/api/v1/comments/{comment_id}", headers=headers2)
    assert response.status_code == 403
