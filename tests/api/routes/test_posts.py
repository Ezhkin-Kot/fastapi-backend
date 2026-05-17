import pytest
from httpx import AsyncClient
from pathlib import Path
import io
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


async def create_post(
    test_app: AsyncClient, token: str, title: str, text: str = "Some text"
):
    headers = {"Authorization": f"Bearer {token}"}
    post_data = {
        "title": title,
        "text": text,
        "pub_date": datetime.now(timezone.utc).isoformat(),  # Added pub_date
    }
    create_post_response = await test_app.post(
        "/api/v1/posts/", headers=headers, json=post_data
    )
    assert create_post_response.status_code == 201
    return create_post_response.json()


@pytest.mark.asyncio
async def test_create_and_get_post(test_app: AsyncClient):
    token, _ = await create_user_and_login(test_app, "post_user")
    post_data = await create_post(test_app, token, "Test Post Title", "Test post text.")

    response = await test_app.get(f"/api/v1/posts/{post_data['id']}")
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["id"] == post_data["id"]
    assert response_data["title"] == "Test Post Title"
    assert "image" in response_data and response_data["image"] is None


@pytest.mark.asyncio
async def test_get_posts_pagination(test_app: AsyncClient):
    token, _ = await create_user_and_login(test_app, "pagination_user")
    # Create 12 posts
    for i in range(12):
        await create_post(test_app, token, f"Post {i+1}")

    # Get first page
    response = await test_app.get("/api/v1/posts/?page=1&size=5")
    assert response.status_code == 200
    paginated_data = response.json()
    assert paginated_data["total"] == 12
    assert paginated_data["page"] == 1
    assert paginated_data["size"] == 5
    assert len(paginated_data["results"]) == 5
    assert paginated_data["results"][0]["title"] == "Post 12"  # Most recent first

    # Get third page
    response = await test_app.get("/api/v1/posts/?page=3&size=5")
    assert response.status_code == 200
    paginated_data = response.json()
    assert paginated_data["total"] == 12
    assert len(paginated_data["results"]) == 2


@pytest.mark.asyncio
async def test_update_post_not_author(test_app: AsyncClient):
    token1, _ = await create_user_and_login(test_app, "post_update_other1")
    token2, _ = await create_user_and_login(test_app, "post_update_other2")

    post = await create_post(test_app, token1, "Original Title")

    headers2 = {"Authorization": f"Bearer {token2}"}
    update_data = {"title": "Updated By Other"}
    response = await test_app.put(
        f"/api/v1/posts/{post['id']}", headers=headers2, json=update_data
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_delete_post_not_author(test_app: AsyncClient):
    token1, _ = await create_user_and_login(test_app, "post_delete_other1")
    token2, _ = await create_user_and_login(test_app, "post_delete_other2")

    post = await create_post(test_app, token1, "Post to be deleted")

    headers2 = {"Authorization": f"Bearer {token2}"}
    response = await test_app.delete(f"/api/v1/posts/{post['id']}", headers=headers2)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_image_upload_and_get(test_app: AsyncClient):
    token, _ = await create_user_and_login(test_app, "image_uploader")
    post = await create_post(test_app, token, "Post with Image")
    post_id = post["id"]

    # Create a fake image file
    fake_image_bytes = b"fake image data"
    files = {"file": ("test_image.png", io.BytesIO(fake_image_bytes), "image/png")}

    # Upload the image
    headers = {"Authorization": f"Bearer {token}"}
    response = await test_app.post(
        f"/api/v1/posts/{post_id}/image", headers=headers, files=files
    )
    assert response.status_code == 200
    response_data = response.json()
    assert "image" in response_data
    image_path = response_data["image"]
    assert image_path is not None
    assert str(post_id) in image_path

    # Get the image
    response = await test_app.get(f"/api/v1/posts/{post_id}/image")
    assert response.status_code == 200
    assert response.content == fake_image_bytes


@pytest.mark.asyncio
async def test_upload_non_image_file_fails(test_app: AsyncClient):
    token, _ = await create_user_and_login(test_app, "non_image_uploader")
    post = await create_post(test_app, token, "Post for bad upload")
    post_id = post["id"]

    files = {"file": ("test.txt", io.BytesIO(b"this is not an image"), "text/plain")}

    headers = {"Authorization": f"Bearer {token}"}
    response = await test_app.post(
        f"/api/v1/posts/{post_id}/image", headers=headers, files=files
    )
    assert response.status_code == 400
