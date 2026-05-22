"""seed initial data

Revision ID: eb6f851fd1cb
Revises: 35c67b909343
Create Date: 2026-05-22 12:19:14.172819

"""

import uuid
from typing import Sequence, Union
from datetime import datetime

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from passlib.context import CryptContext

# revision identifiers, used by Alembic.
revision: str = "eb6f851fd1cb"
down_revision: Union[str, Sequence[str], None] = "35c67b909343"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Setup password context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Define table helpers
users_table = sa.table(
    "users",
    sa.column("id", postgresql.UUID(as_uuid=True)),
    sa.column("first_name", sa.String),
    sa.column("last_name", sa.String),
    sa.column("username", sa.String),
    sa.column("email", sa.String),
    sa.column("hashed_password", sa.String),
    sa.column("is_active", sa.Boolean),
    sa.column("is_superuser", sa.Boolean),
)

locations_table = sa.table(
    "locations",
    sa.column("id", postgresql.UUID(as_uuid=True)),
    sa.column("name", sa.String),
    sa.column("is_published", sa.Boolean),
)

categories_table = sa.table(
    "categories",
    sa.column("id", postgresql.UUID(as_uuid=True)),
    sa.column("title", sa.String),
    sa.column("slug", sa.String),
    sa.column("description", sa.String),
    sa.column("is_published", sa.Boolean),
)

posts_table = sa.table(
    "posts",
    sa.column("id", postgresql.UUID(as_uuid=True)),
    sa.column("title", sa.String),
    sa.column("text", sa.String),
    sa.column("author_id", postgresql.UUID(as_uuid=True)),
    sa.column("category_id", postgresql.UUID(as_uuid=True)),
    sa.column("location_id", postgresql.UUID(as_uuid=True)),
    sa.column("is_published", sa.Boolean),
    sa.column("pub_date", sa.DateTime),
)

comments_table = sa.table(
    "comments",
    sa.column("id", postgresql.UUID(as_uuid=True)),
    sa.column("text", sa.String),
    sa.column("author_id", postgresql.UUID(as_uuid=True)),
    sa.column("post_id", postgresql.UUID(as_uuid=True)),
)


def upgrade() -> None:
    """Seed the database with initial data. This migration is idempotent."""
    # Clear any existing seed data first to ensure idempotency
    op.execute(
        "DELETE FROM comments WHERE text IN ('CommentText1', 'CommentText2', 'CommentText3')"
    )
    op.execute(
        "DELETE FROM posts WHERE title IN ('PostTitle1', 'PostTitle2', 'PostTitle3', 'PostTitle4', 'PostTitle5', 'PostTitle6', 'PostTitle7', 'PostTitle8', 'PostTitle9', 'PostTitle10', 'PostTitle11')"
    )
    op.execute(
        "DELETE FROM categories WHERE slug IN ('cat-title1', 'cat-title2', 'cat-title3')"
    )
    op.execute(
        "DELETE FROM locations WHERE name IN ('TestLoc1', 'TestLoc2', 'TestLoc3')"
    )
    op.execute("DELETE FROM users WHERE username IN ('admin', 'test1', 'test2')")

    # Generate UUIDs
    user_admin_id = uuid.uuid4()
    user_test1_id = uuid.uuid4()
    user_test2_id = uuid.uuid4()

    loc_test1_id = uuid.uuid4()
    loc_test2_id = uuid.uuid4()
    loc_test3_id = uuid.uuid4()

    cat_test1_id = uuid.uuid4()
    cat_test2_id = uuid.uuid4()
    cat_test3_id = uuid.uuid4()

    post_ids = [uuid.uuid4() for _ in range(11)]

    # --- Seed Users ---
    op.bulk_insert(
        users_table,
        [
            {
                "id": user_admin_id,
                "first_name": "Admin",
                "last_name": "TestUser",
                "username": "admin",
                "email": "admin@example.com",
                "hashed_password": pwd_context.hash("adminpassword"),
                "is_active": True,
                "is_superuser": True,
            },
            {
                "id": user_test1_id,
                "first_name": "Test1",
                "last_name": "TestUser",
                "username": "test1",
                "email": "test1@example.com",
                "hashed_password": pwd_context.hash("test1password"),
                "is_active": True,
                "is_superuser": False,
            },
            {
                "id": user_test2_id,
                "first_name": "Test2",
                "last_name": "TestUser",
                "username": "test2",
                "email": "test2@example.com",
                "hashed_password": pwd_context.hash("test1password"),
                "is_active": True,
                "is_superuser": False,
            },
        ],
    )

    # --- Seed Locations ---
    op.bulk_insert(
        locations_table,
        [
            {"id": loc_test1_id, "name": "TestLoc1", "is_published": True},
            {"id": loc_test2_id, "name": "TestLoc2", "is_published": True},
            {"id": loc_test3_id, "name": "TestLoc3", "is_published": True},
        ],
    )

    # --- Seed Categories ---
    op.bulk_insert(
        categories_table,
        [
            {
                "id": cat_test1_id,
                "title": "CategoryTitle1",
                "slug": "cat-title1",
                "description": "Description for Category 1",
                "is_published": True,
            },
            {
                "id": cat_test2_id,
                "title": "CategoryTitle2",
                "slug": "cat-title2",
                "description": "Description for Category 2",
                "is_published": True,
            },
            {
                "id": cat_test3_id,
                "title": "CategoryTitle3",
                "slug": "cat-title3",
                "description": "Description for Category 3",
                "is_published": True,
            },
        ],
    )

    # --- Seed Posts ---
    posts_data = [
        {
            "id": post_ids[0],
            "title": "PostTitle1",
            "text": "Text for PostTitle1",
            "author_id": user_test1_id,
            "category_id": cat_test1_id,
            "location_id": loc_test1_id,
            "is_published": True,
            "pub_date": datetime.utcnow(),
        },
        {
            "id": post_ids[1],
            "title": "PostTitle2",
            "text": "Text for PostTitle2",
            "author_id": user_test2_id,
            "category_id": cat_test2_id,
            "location_id": loc_test2_id,
            "is_published": True,
            "pub_date": datetime.utcnow(),
        },
        {
            "id": post_ids[2],
            "title": "PostTitle3",
            "text": "Text for PostTitle3",
            "author_id": user_admin_id,
            "category_id": cat_test3_id,
            "location_id": loc_test3_id,
            "is_published": True,
            "pub_date": datetime.utcnow(),
        },
        {
            "id": post_ids[3],
            "title": "PostTitle4",
            "text": "Text for PostTitle4",
            "author_id": user_test1_id,
            "category_id": cat_test1_id,
            "location_id": loc_test1_id,
            "is_published": True,
            "pub_date": datetime.utcnow(),
        },
        {
            "id": post_ids[4],
            "title": "PostTitle5",
            "text": "Text for PostTitle5",
            "author_id": user_test2_id,
            "category_id": cat_test2_id,
            "location_id": loc_test2_id,
            "is_published": True,
            "pub_date": datetime.utcnow(),
        },
        {
            "id": post_ids[5],
            "title": "PostTitle6",
            "text": "Text for PostTitle6",
            "author_id": user_admin_id,
            "category_id": cat_test3_id,
            "location_id": loc_test3_id,
            "is_published": True,
            "pub_date": datetime.utcnow(),
        },
        {
            "id": post_ids[6],
            "title": "PostTitle7",
            "text": "Text for PostTitle7",
            "author_id": user_test1_id,
            "category_id": cat_test1_id,
            "location_id": loc_test1_id,
            "is_published": True,
            "pub_date": datetime.utcnow(),
        },
        {
            "id": post_ids[7],
            "title": "PostTitle8",
            "text": "Text for PostTitle8",
            "author_id": user_test2_id,
            "category_id": cat_test2_id,
            "location_id": loc_test2_id,
            "is_published": True,
            "pub_date": datetime.utcnow(),
        },
        {
            "id": post_ids[8],
            "title": "PostTitle9",
            "text": "Text for PostTitle9",
            "author_id": user_admin_id,
            "category_id": cat_test3_id,
            "location_id": loc_test3_id,
            "is_published": True,
            "pub_date": datetime.utcnow(),
        },
        {
            "id": post_ids[9],
            "title": "PostTitle10",
            "text": "Text for PostTitle10",
            "author_id": user_test1_id,
            "category_id": cat_test1_id,
            "location_id": loc_test1_id,
            "is_published": True,
            "pub_date": datetime.utcnow(),
        },
        {
            "id": post_ids[10],
            "title": "PostTitle11",
            "text": "Text for PostTitle11",
            "author_id": user_test2_id,
            "category_id": cat_test2_id,
            "location_id": loc_test2_id,
            "is_published": True,
            "pub_date": datetime.utcnow(),
        },
    ]
    op.bulk_insert(posts_table, posts_data)

    # --- Seed Comments ---
    op.bulk_insert(
        comments_table,
        [
            {
                "id": uuid.uuid4(),
                "text": "CommentText1",
                "author_id": user_test1_id,
                "post_id": post_ids[0],
            },
            {
                "id": uuid.uuid4(),
                "text": "CommentText2",
                "author_id": user_test2_id,
                "post_id": post_ids[0],
            },
            {
                "id": uuid.uuid4(),
                "text": "CommentText3",
                "author_id": user_test1_id,
                "post_id": post_ids[1],
            },
        ],
    )


def downgrade() -> None:
    """Remove the initial seed data."""
    # The order of deletion is important to respect foreign key constraints.
    op.execute(
        "DELETE FROM comments WHERE text IN ('CommentText1', 'CommentText2', 'CommentText3')"
    )
    op.execute(
        "DELETE FROM posts WHERE title IN ('PostTitle1', 'PostTitle2', 'PostTitle3', 'PostTitle4', 'PostTitle5', 'PostTitle6', 'PostTitle7', 'PostTitle8', 'PostTitle9', 'PostTitle10', 'PostTitle11')"
    )
    op.execute(
        "DELETE FROM categories WHERE slug IN ('cat-title1', 'cat-title2', 'cat-title3')"
    )
    op.execute(
        "DELETE FROM locations WHERE name IN ('TestLoc1', 'TestLoc2', 'TestLoc3')"
    )
    op.execute("DELETE FROM users WHERE username IN ('admin', 'test1', 'test2')")
