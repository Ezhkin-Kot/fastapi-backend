from src.core.exceptions import NotFoundError
from src.db.db import database
from src.db.models.posts import Post
from src.db.models.users import User
from src.db.repositories.categories import CategoryRepository
from src.db.repositories.locations import LocationRepository
from src.db.repositories.posts import PostRepository
from src.schemas.posts import PostCreate


class CreatePostUseCase:
    def __init__(self):
        pass

    async def execute(self, post_in: PostCreate, author: User) -> Post:
        async with database.session() as session:
            post_repo = PostRepository(session)
            category_repo = CategoryRepository(session)
            location_repo = LocationRepository(session)

            if post_in.category_id:
                category = await category_repo.get(post_in.category_id)
                if not category:
                    raise NotFoundError(
                        f"Category with id {post_in.category_id} not found"
                    )

            if post_in.location_id:
                location = await location_repo.get(post_in.location_id)
                if not location:
                    raise NotFoundError(
                        f"Location with id {post_in.location_id} not found"
                    )

            post_data = post_in.model_dump()
            post_data["author_id"] = author.id
            new_post = await post_repo.create(post_data)
            await session.flush()
            await session.refresh(new_post, attribute_names=["comments"])
            return new_post
