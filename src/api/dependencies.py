from src.domain.post.use_cases.create_post import CreatePostUseCase
from src.domain.post.use_cases.get_posts import GetPostsUseCase
from src.domain.post.use_cases.get_post import GetPostUseCase
from src.domain.post.use_cases.delete_post import DeletePostUseCase
from src.domain.post.use_cases.update_post import UpdatePostUseCase
from src.domain.auth.use_cases.create_access_token import CreateAccessTokenUseCase
from src.domain.auth.use_cases.authenticate_user import AuthenticateUserUseCase
from src.domain.comment.use_cases.create_comment import CreateCommentUseCase
from src.domain.comment.use_cases.get_comments import GetCommentsUseCase
from src.domain.user.use_cases.create_user import CreateUserUseCase


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


def create_access_token_use_case() -> CreateAccessTokenUseCase:
    return CreateAccessTokenUseCase()


def authenticate_user_use_case() -> AuthenticateUserUseCase:
    return AuthenticateUserUseCase()


def create_comment_use_case() -> CreateCommentUseCase:
    return CreateCommentUseCase()


def get_comments_use_case() -> GetCommentsUseCase:
    return GetCommentsUseCase()


def create_user_use_case() -> CreateUserUseCase:
    return CreateUserUseCase()
