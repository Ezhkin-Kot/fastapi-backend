import pytest
from httpx import AsyncClient

from tests.helpers import (
    create_user_directly,
    login_user,
    create_category,
    create_post,
    create_user_and_login,
)


@pytest.mark.asyncio
async def test_get_and_list_categories(test_app: AsyncClient):
    # Setup: Create an admin and some categories
    admin_data = await create_user_directly("cat_list_admin", is_superuser=True)
    admin_token_data = await login_user(
        test_app, admin_data["username"], admin_data["password"]
    )
    admin_access_token = admin_token_data["access_token"]
    cat1 = await create_category(test_app, admin_access_token, "cat-1", "Category 1")
    await create_category(test_app, admin_access_token, "cat-2", "Category 2")

    # Test Get single category (public endpoint)
    response = await test_app.get(f"/api/v1/categories/{cat1['id']}")
    assert response.status_code == 200
    assert response.json()["slug"] == "cat-1"

    # Test Get all categories (public endpoint)
    response = await test_app.get("/api/v1/categories/")
    assert response.status_code == 200
    category_list = response.json()
    assert isinstance(category_list, list)
    assert len(category_list) >= 2
    slugs = {c["slug"] for c in category_list}
    assert "cat-1" in slugs
    assert "cat-2" in slugs


@pytest.mark.asyncio
async def test_get_posts_by_category(test_app: AsyncClient):
    # Setup: Create admin, regular user, categories, and posts
    admin_data = await create_user_directly("cat_posts_admin", is_superuser=True)
    admin_token_data = await login_user(
        test_app, admin_data["username"], admin_data["password"]
    )
    admin_access_token = admin_token_data["access_token"]
    user_token, _ = await create_user_and_login(test_app, "cat_posts_user")

    tech_cat = await create_category(test_app, admin_access_token, "tech", "Technology")
    life_cat = await create_category(
        test_app, admin_access_token, "lifestyle", "Lifestyle"
    )

    await create_post(
        test_app, user_token, "Post 1 in Tech", category_id=tech_cat["id"]
    )
    await create_post(
        test_app, user_token, "Post 2 in Tech", category_id=tech_cat["id"]
    )
    await create_post(
        test_app, user_token, "Post 3 in Lifestyle", category_id=life_cat["id"]
    )

    # Test Get posts for 'tech' category (public endpoint)
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
