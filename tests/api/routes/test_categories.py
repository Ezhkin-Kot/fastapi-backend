import pytest
from httpx import AsyncClient

from tests.helpers import create_user_and_login, create_category, create_post


@pytest.mark.asyncio
async def test_category_crud_permissions(test_app: AsyncClient):
    # Non-admin user
    user_token, _ = await create_user_and_login(test_app, "cat_user")
    # Admin user
    admin_token, _ = await create_user_and_login(
        test_app, "cat_admin", is_superuser=True
    )

    headers_user = {"Authorization": f"Bearer {user_token}"}
    headers_admin = {"Authorization": f"Bearer {admin_token}"}

    category_data = {
        "title": "Test Category",
        "description": "desc",
        "slug": "test-cat",
    }

    # Non-admin fails to create
    response = await test_app.post(
        "/api/v1/categories/", headers=headers_user, json=category_data
    )
    assert response.status_code == 403

    # Admin creates successfully
    response = await test_app.post(
        "/api/v1/categories/", headers=headers_admin, json=category_data
    )
    assert response.status_code == 200
    category = response.json()
    category_id = category["id"]

    # Non-admin fails to update
    response = await test_app.put(
        f"/api/v1/categories/{category_id}",
        headers=headers_user,
        json={"title": "New Title"},
    )
    assert response.status_code == 403

    # Admin updates successfully
    response = await test_app.put(
        f"/api/v1/categories/{category_id}",
        headers=headers_admin,
        json={"title": "New Title"},
    )
    assert response.status_code == 200
    assert response.json()["title"] == "New Title"

    # Non-admin fails to delete
    response = await test_app.delete(
        f"/api/v1/categories/{category_id}", headers=headers_user
    )
    assert response.status_code == 403

    # Admin deletes successfully
    response = await test_app.delete(
        f"/api/v1/categories/{category_id}", headers=headers_admin
    )
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_get_and_list_categories(test_app: AsyncClient):
    admin_token, _ = await create_user_and_login(
        test_app, "cat_list_admin", is_superuser=True
    )
    cat1 = await create_category(test_app, admin_token, "cat-1", "Category 1")
    cat2 = await create_category(test_app, admin_token, "cat-2", "Category 2")

    # Get single category
    response = await test_app.get(f"/api/v1/categories/{cat1['id']}")
    assert response.status_code == 200
    assert response.json()["slug"] == "cat-1"

    # Get all categories (paginated)
    response = await test_app.get("/api/v1/categories/")
    assert response.status_code == 200
    paginated_data = response.json()
    assert paginated_data["total"] >= 2
    slugs = {c["slug"] for c in paginated_data["results"]}
    assert "cat-1" in slugs
    assert "cat-2" in slugs


@pytest.mark.asyncio
async def test_get_posts_by_category(test_app: AsyncClient):
    admin_token, _ = await create_user_and_login(
        test_app, "cat_posts_admin", is_superuser=True
    )
    user_token, _ = await create_user_and_login(test_app, "cat_posts_user")

    tech_cat = await create_category(test_app, admin_token, "tech", "Technology")
    life_cat = await create_category(test_app, admin_token, "lifestyle", "Lifestyle")

    # Create posts
    await create_post(
        test_app, user_token, "Post 1 in Tech", category_id=tech_cat["id"]
    )
    await create_post(
        test_app, user_token, "Post 2 in Tech", category_id=tech_cat["id"]
    )
    await create_post(
        test_app, user_token, "Post 3 in Lifestyle", category_id=life_cat["id"]
    )

    # Get posts for 'tech' category
    response = await test_app.get("/api/v1/categories/tech/posts")
    assert response.status_code == 200
    paginated_response = response.json()
    assert paginated_response["total"] == 2
    assert len(paginated_response["results"]) == 2
    assert {p["title"] for p in paginated_response["results"]} == {
        "Post 1 in Tech",
        "Post 2 in Tech",
    }

    # Test pagination for category posts
    response = await test_app.get("/api/v1/categories/tech/posts?page=2&size=1")
    assert response.status_code == 200
    paginated_response = response.json()
    assert paginated_response["total"] == 2
    assert len(paginated_response["results"]) == 1
