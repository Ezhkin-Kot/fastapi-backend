from httpx import AsyncClient
import pytest
from datetime import datetime, timezone

@pytest.mark.asyncio
async def test_create_comment(test_app):
    user_data = {
        "first_name": "Test",
        "last_name": "User",
        "username": "testuser_comment",
        "email": "testuser_comment@example.com",
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

    # Create post
    headers = {"Authorization": f"Bearer {token}"}
    post_data = {
        "title": "Test Post for Comment",
        "text": "This is a test post for comment.",
        "pub_date": datetime.now(timezone.utc).isoformat()
    }
    create_post_response = await test_app.post("/api/v1/posts/", headers=headers, json=post_data)
    assert create_post_response.status_code == 201
    post_id = create_post_response.json()["id"]

    # Create comment
    comment_data = {"text": "This is a test comment."}
    response = await test_app.post(f"/api/v1/posts/{post_id}/comments/", headers=headers, json=comment_data)
    assert response.status_code == 201
    response_data = response.json()
    assert response_data["text"] == comment_data["text"]
    assert "id" in response_data


@pytest.mark.asyncio
async def test_get_comments(test_app):
    user_data = {
        "first_name": "Test",
        "last_name": "User",
        "username": "testuser_get_comments",
        "email": "testuser_get_comments@example.com",
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

    # Create post
    headers = {"Authorization": f"Bearer {token}"}
    post_data = {
        "title": "Test Post for Comments",
        "text": "This is a test post for comments.",
        "pub_date": datetime.now(timezone.utc).isoformat()
    }
    create_post_response = await test_app.post("/api/v1/posts/", headers=headers, json=post_data)
    assert create_post_response.status_code == 201
    post_id = create_post_response.json()["id"]

    # Create comments
    comment1_data = {"text": "This is a test comment 1."}
    comment2_data = {"text": "This is a test comment 2."}
    await test_app.post(f"/api/v1/posts/{post_id}/comments/", headers=headers, json=comment1_data)
    await test_app.post(f"/api/v1/posts/{post_id}/comments/", headers=headers, json=comment2_data)

    # Get all comments
    response = await test_app.get(f"/api/v1/posts/{post_id}/comments/")
    assert response.status_code == 200
    response_data = response.json()
    assert len(response_data) >= 2
    texts = [comment["text"] for comment in response_data]
    assert comment1_data["text"] in texts
    assert comment2_data["text"] in texts
