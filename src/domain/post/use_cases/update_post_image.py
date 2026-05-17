import uuid

from src.db.db import database
from src.db.models.posts import Post
from src.db.models.users import User
from src.db.repositories.posts import PostRepository
from src.core.exceptions import NotFoundError, ForbiddenError


class UpdatePostImageUseCase:
    def __init__(self):
        pass

    async def execute(
        self, post_id: uuid.UUID, image_path: str, current_user: User
    ) -> Post:
        async with database.session() as session:
            repo = PostRepository(session)
            post = await repo.get(post_id)
            if not post:
                raise NotFoundError(message="Post not found")

            if post.author_id != current_user.id:
                raise ForbiddenError(message="You can only update your own posts")

            update_data = {"image": image_path}
            updated_post = await repo.update(post, update_data)
            return updated_post
