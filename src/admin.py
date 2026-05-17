from typing import Any

from fastapi import Request
from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend

from src.db.models import Category, Comment, Location, Post, User
from src.services.auth import get_current_user, Token
from src.api.dependencies import (
    authenticate_user_use_case,
    create_access_token_use_case,
)


class AdminAuthBackend(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username = form.get("username")
        password = form.get("password")

        auth_use_case = authenticate_user_use_case()
        user = await auth_use_case.execute(username, password)

        if not user or not user.is_superuser:
            return False

        token_use_case = create_access_token_use_case()
        access_token = token_use_case.execute(data={"sub": user.username})

        request.session.update({"token": access_token})
        return True

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("token")
        if not token:
            return False

        try:
            user = await get_current_user(token=token)
            if not user or not user.is_superuser:
                return False
        except Exception:
            return False

        return True


class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.username, User.email, User.is_superuser]
    column_searchable_list = [User.username, User.email]
    column_sortable_list = [User.id, User.username, User.email]
    can_create = True
    can_edit = True
    can_delete = False
    icon = "fa-solid fa-user"


class PostAdmin(ModelView, model=Post):
    column_list = [Post.id, Post.title, Post.author, Post.is_published, Post.pub_date]
    column_searchable_list = [Post.title, Post.text]
    column_sortable_list = [Post.pub_date, Post.created_at]
    column_formatters = {
        Post.text: lambda m, a: (
            m.text[:100] + "..." if m.text and len(m.text) > 100 else m.text
        )
    }
    can_create = True
    can_edit = True
    can_delete = True
    icon = "fa-solid fa-file-pen"


class CommentAdmin(ModelView, model=Comment):
    column_list = [Comment.id, Comment.author, Comment.post, Comment.created_at]
    column_searchable_list = [Comment.text]
    column_sortable_list = [Comment.created_at]
    can_create = False
    can_edit = True
    can_delete = True
    icon = "fa-solid fa-comment"


class CategoryAdmin(ModelView, model=Category):
    column_list = [Category.id, Category.title, Category.slug, Category.is_published]
    column_searchable_list = [Category.title, Category.slug]
    can_create = True
    can_edit = True
    can_delete = True
    icon = "fa-solid fa-folder"


class LocationAdmin(ModelView, model=Location):
    column_list = [Location.id, Location.name, Location.is_published]
    column_searchable_list = [Location.name]
    can_create = True
    can_edit = True
    can_delete = True
    icon = "fa-solid fa-location-dot"
