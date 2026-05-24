from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.db import get_session
from src.db.redis import get_redis_client
from src.db.repositories.users import UserRepository
from src.domain.post.use_cases.create_post import CreatePostUseCase
from src.domain.post.use_cases.get_posts import GetPostsUseCase
from src.domain.post.use_cases.get_post import GetPostUseCase
from src.domain.post.use_cases.delete_post import DeletePostUseCase
from src.domain.post.use_cases.update_post import UpdatePostUseCase
from src.domain.post.use_cases.get_posts_by_category import GetPostsByCategoryUseCase
from src.domain.post.use_cases.get_posts_by_user import GetPostsByUserUseCase
from src.domain.post.use_cases.update_post_image import UpdatePostImageUseCase
from src.domain.auth.use_cases.create_access_token import CreateAccessTokenUseCase
from src.domain.auth.use_cases.authenticate_user import AuthenticateUserUseCase
from src.domain.auth.use_cases.refresh_token import RefreshTokenUseCase
from src.domain.auth.use_cases.logout_user import LogoutUserUseCase
from src.domain.comment.use_cases.create_comment import CreateCommentUseCase
from src.domain.comment.use_cases.get_comments import GetCommentsUseCase
from src.domain.comment.use_cases.update_comment import UpdateCommentUseCase
from src.domain.comment.use_cases.delete_comment import DeleteCommentUseCase
from src.domain.user.use_cases.create_user import CreateUserUseCase
from src.domain.user.use_cases.get_user import GetUserUseCase
from src.domain.category.use_cases.create_category import CreateCategoryUseCase
from src.domain.category.use_cases.get_categories import GetCategoriesUseCase
from src.domain.category.use_cases.get_category import GetCategoryUseCase
from src.domain.category.use_cases.update_category import UpdateCategoryUseCase
from src.domain.category.use_cases.delete_category import DeleteCategoryUseCase
from redis.asyncio import Redis


def create_post_use_case() -> CreatePostUseCase:
    return CreatePostUseCase()


def get_posts_use_case() -> GetPostsUseCase:
    return GetPostsUseCase()


def get_post_use_case() -> GetPostUseCase:
    return GetPostUseCase()


def delete_post_use_case() -> DeletePostUseCase:
    return DeletePostUseCase()


def update_post_use_case() -> UpdatePostUseCase:
    return UpdatePostUseCase()


def get_posts_by_category_use_case() -> GetPostsByCategoryUseCase:
    return GetPostsByCategoryUseCase()


def get_posts_by_user_use_case() -> GetPostsByUserUseCase:
    return GetPostsByUserUseCase()


def update_post_image_use_case() -> UpdatePostImageUseCase:
    return UpdatePostImageUseCase()


def create_access_token_use_case() -> CreateAccessTokenUseCase:
    return CreateAccessTokenUseCase()


def authenticate_user_use_case(
    session: AsyncSession = Depends(get_session),
    redis_client: Redis = Depends(get_redis_client),
    create_access_token_use_case: CreateAccessTokenUseCase = Depends(
        create_access_token_use_case
    ),
) -> AuthenticateUserUseCase:
    return AuthenticateUserUseCase(
        create_access_token_use_case=create_access_token_use_case,
        session=session,
        redis_client=redis_client,
    )


def refresh_token_use_case(
    session: AsyncSession = Depends(get_session),
    redis_client: Redis = Depends(get_redis_client),
    create_access_token_use_case: CreateAccessTokenUseCase = Depends(
        create_access_token_use_case
    ),
) -> RefreshTokenUseCase:
    return RefreshTokenUseCase(
        create_access_token_use_case=create_access_token_use_case,
        user_repository=UserRepository(session),
        redis_client=redis_client,
    )


def logout_user_use_case(
    redis_client: Redis = Depends(get_redis_client),
) -> LogoutUserUseCase:
    return LogoutUserUseCase(
        redis_client=redis_client,
    )


def create_comment_use_case() -> CreateCommentUseCase:
    return CreateCommentUseCase()


def get_comments_use_case() -> GetCommentsUseCase:
    return GetCommentsUseCase()


def update_comment_use_case() -> UpdateCommentUseCase:
    return UpdateCommentUseCase()


def delete_comment_use_case() -> DeleteCommentUseCase:
    return DeleteCommentUseCase()


def create_user_use_case() -> CreateUserUseCase:
    return CreateUserUseCase()


def get_user_use_case() -> GetUserUseCase:
    return GetUserUseCase()


def create_category_use_case() -> CreateCategoryUseCase:
    return CreateCategoryUseCase()


def get_categories_use_case() -> GetCategoriesUseCase:
    return GetCategoriesUseCase()


def get_category_use_case() -> GetCategoryUseCase:
    return GetCategoryUseCase()


def update_category_use_case() -> UpdateCategoryUseCase:
    return UpdateCategoryUseCase()


def delete_category_use_case() -> DeleteCategoryUseCase:
    return DeleteCategoryUseCase()
