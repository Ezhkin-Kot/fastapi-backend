from src.db.db import database
from src.schemas.posts import PostCreate
from src.db.models.posts import Post
from src.db.models.users import User
from src.db.repositories.posts import PostRepository


class CreatePostUseCase:
    def __init__(self):
        pass

    async def execute(self, post_in: PostCreate, author: User) -> Post:
        async with database.session() as session:
            self.repository = PostRepository(session)
            post_data = post_in.model_dump()
            post_data["author_id"] = author.id
            new_post = await self.repository.create(post_data)
            return new_post
