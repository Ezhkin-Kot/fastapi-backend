from sqlalchemy.ext.asyncio import AsyncSession

from schemas.posts import PostCreate
from models.posts import Post
from models.users import User
from repositories.posts import PostRepository


class CreatePostUseCase:
    def __init__(self, session: AsyncSession):
        self.repository = PostRepository(session)

    async def execute(self, post_in: PostCreate, author: User) -> Post:
        post_data = post_in.model_dump()
        post_data["author_id"] = author.id
        new_post = await self.repository.create(post_data)
        return new_post
