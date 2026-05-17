import pytest
from httpx import AsyncClient
from tests.helpers import create_user_and_login, create_comment, create_post


@pytest.mark.asyncio
async def test_create_and_get_comments(test_app: AsyncClient):
    token, _ = await create_user_and_login(test_app, "comments_user")
    post = await create_post(test_app, token, "Post for Comments")
    post_id = post["id"]

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
    post = await create_post(test_app, token, "Post for comment update")
    post_id = post["id"]
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
    post = await create_post(test_app, token1, "Post for comment update fail")
    post_id = post["id"]
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
    post = await create_post(test_app, token, "Post for comment delete")
    post_id = post["id"]
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
    post = await create_post(test_app, token1, "Post for comment delete fail")
    post_id = post["id"]
    comment_id = await create_comment(test_app, token1, post_id, "User 1 comment")

    token2, _ = await create_user_and_login(test_app, "delete_not_author2")

    headers2 = {"Authorization": f"Bearer {token2}"}
    response = await test_app.delete(f"/api/v1/comments/{comment_id}", headers=headers2)
    assert response.status_code == 403
