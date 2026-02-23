from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from api.routes.users import router as users_router
from api.routes.posts import router as posts_router


def create_app() -> FastAPI:
    app = FastAPI(root_path="/api/v1")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(users_router, prefix="/users", tags=["Users"])
    app.include_router(posts_router, prefix="/posts", tags=["Posts"])

    return app
