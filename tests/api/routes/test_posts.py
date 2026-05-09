from httpx import AsyncClient
import pytest
from datetime import datetime, timezone

@pytest.mark.asyncio
async def test_create_post(test_app):
    user_data = {
        "first_name": "Test",
        "last_name": "User",
        "username": "testuser_post",
        "email": "testuser_post@example.com",
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
        "title": "Test Post",
        "text": "This is a test post.",
        "pub_date": datetime.now(timezone.utc).isoformat()
    }
    response = await test_app.post("/api/v1/posts/", headers=headers, json=post_data)
    assert response.status_code == 201
    response_data = response.json()
    assert response_data["title"] == post_data["title"]
    assert response_data["text"] == post_data["text"]
    assert "id" in response_data


@pytest.mark.asyncio
async def test_get_posts(test_app):
    user_data = {
        "first_name": "Test",
        "last_name": "User",
        "username": "testuser_get_posts",
        "email": "testuser_get_posts@example.com",
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

    # Create posts
    headers = {"Authorization": f"Bearer {token}"}
    post1_data = {
        "title": "Test Post 1",
        "text": "This is a test post 1.",
        "pub_date": datetime.now(timezone.utc).isoformat()
    }
    post2_data = {
        "title": "Test Post 2",
        "text": "This is a test post 2.",
        "pub_date": datetime.now(timezone.utc).isoformat()
    }
    await test_app.post("/api/v1/posts/", headers=headers, json=post1_data)
    await test_app.post("/api/v1/posts/", headers=headers, json=post2_data)

    # Get all posts
    response = await test_app.get("/api/v1/posts/", headers=headers)
    assert response.status_code == 200
    response_data = response.json()
    assert len(response_data) >= 2
    titles = [post["title"] for post in response_data]
    assert post1_data["title"] in titles
    assert post2_data["title"] in titles


@pytest.mark.asyncio
async def test_get_post(test_app):
    user_data = {
        "first_name": "Test",
        "last_name": "User",
        "username": "testuser_get_post",
        "email": "testuser_get_post@example.com",
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
        "title": "Test Post",
        "text": "This is a test post.",
        "pub_date": datetime.now(timezone.utc).isoformat()
    }
    create_response = await test_app.post("/api/v1/posts/", headers=headers, json=post_data)
    assert create_response.status_code == 201
    post_id = create_response.json()["id"]

    # Get post
    response = await test_app.get(f"/api/v1/posts/{post_id}", headers=headers)
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["id"] == post_id
    assert response_data["title"] == post_data["title"]
    assert response_data["text"] == post_data["text"]


@pytest.mark.asyncio
async def test_update_post(test_app):
    user_data = {
        "first_name": "Test",
        "last_name": "User",
        "username": "testuser_update_post",
        "email": "testuser_update_post@example.com",
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
        "title": "Test Post",
        "text": "This is a test post.",
        "pub_date": datetime.now(timezone.utc).isoformat()
    }
    create_response = await test_app.post("/api/v1/posts/", headers=headers, json=post_data)
    assert create_response.status_code == 201
    post_id = create_response.json()["id"]

    # Update post
    update_data = {"title": "Updated Post"}
    response = await test_app.put(f"/api/v1/posts/{post_id}", headers=headers, json=update_data)
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["title"] == "Updated Post"


@pytest.mark.asyncio
async def test_update_post_not_author(test_app):
    user1_data = {
        "first_name": "Test",
        "last_name": "User1",
        "username": "testuser1_update_post_not_author",
        "email": "testuser1_update_post_not_author@example.com",
        "password": "Password123"
    }
    user2_data = {
        "first_name": "Test",
        "last_name": "User2",
        "username": "testuser2_update_post_not_author",
        "email": "testuser2_update_post_not_author@example.com",
        "password": "Password123"
    }
    # Register users
    await test_app.post("/api/v1/users/register", json=user1_data)
    await test_app.post("/api/v1/users/register", json=user2_data)

    # Login user 1 to get token
    login_data1 = {
        "username": user1_data["username"],
        "password": user1_data["password"]
    }
    response = await test_app.post("/api/v1/auth/token", data=login_data1)
    assert response.status_code == 200
    token1 = response.json()["access_token"]

    # Login user 2 to get token
    login_data2 = {
        "username": user2_data["username"],
        "password": user2_data["password"]
    }
    response = await test_app.post("/api/v1/auth/token", data=login_data2)
    assert response.status_code == 200
    token2 = response.json()["access_token"]

    # User 1 creates post
    headers1 = {"Authorization": f"Bearer {token1}"}
    post_data = {
        "title": "Test Post",
        "text": "This is a test post.",
        "pub_date": datetime.now(timezone.utc).isoformat()
    }
    create_response = await test_app.post("/api/v1/posts/", headers=headers1, json=post_data)
    assert create_response.status_code == 201
    post_id = create_response.json()["id"]

    # User 2 tries to update post
    headers2 = {"Authorization": f"Bearer {token2}"}
    update_data = {"title": "Updated Post"}
    response = await test_app.put(f"/api/v1/posts/{post_id}", headers=headers2, json=update_data)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_delete_post(test_app):
    user_data = {
        "first_name": "Test",
        "last_name": "User",
        "username": "testuser_delete_post",
        "email": "testuser_delete_post@example.com",
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
        "title": "Test Post",
        "text": "This is a test post.",
        "pub_date": datetime.now(timezone.utc).isoformat()
    }
    create_response = await test_app.post("/api/v1/posts/", headers=headers, json=post_data)
    assert create_response.status_code == 201
    post_id = create_response.json()["id"]

    # Delete post
    response = await test_app.delete(f"/api/v1/posts/{post_id}", headers=headers)
    assert response.status_code == 204

    # Verify delete
    response = await test_app.get(f"/api/v1/posts/{post_id}", headers=headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_post_not_author(test_app):
    user1_data = {
        "first_name": "Test",
        "last_name": "User1",
        "username": "testuser1_delete_post_not_author",
        "email": "testuser1_delete_post_not_author@example.com",
        "password": "Password123"
    }
    user2_data = {
        "first_name": "Test",
        "last_name": "User2",
        "username": "testuser2_delete_post_not_author",
        "email": "testuser2_delete_post_not_author@example.com",
        "password": "Password123"
    }
    # Register users
    await test_app.post("/api/v1/users/register", json=user1_data)
    await test_app.post("/api/v1/users/register", json=user2_data)

    # Login user 1 to get token
    login_data1 = {
        "username": user1_data["username"],
        "password": user1_data["password"]
    }
    response = await test_app.post("/api/v1/auth/token", data=login_data1)
    assert response.status_code == 200
    token1 = response.json()["access_token"]

    # Login user 2 to get token
    login_data2 = {
        "username": user2_data["username"],
        "password": user2_data["password"]
    }
    response = await test_app.post("/api/v1/auth/token", data=login_data2)
    assert response.status_code == 200
    token2 = response.json()["access_token"]

    # User 1 creates post
    headers1 = {"Authorization": f"Bearer {token1}"}
    post_data = {
        "title": "Test Post",
        "text": "This is a test post.",
        "pub_date": datetime.now(timezone.utc).isoformat()
    }
    create_response = await test_app.post("/api/v1/posts/", headers=headers1, json=post_data)
    assert create_response.status_code == 201
    post_id = create_response.json()["id"]

    # User 2 tries to delete post
    headers2 = {"Authorization": f"Bearer {token2}"}
    response = await test_app.delete(f"/api/v1/posts/{post_id}", headers=headers2)
    assert response.status_code == 403
