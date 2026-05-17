import logging

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.staticfiles import StaticFiles
from sqladmin import Admin

from src.admin import (
    AdminAuthBackend,
    UserAdmin,
    PostAdmin,
    CategoryAdmin,
    CommentAdmin,
    LocationAdmin,
)
from src.api.routes.posts import router as posts_router
from src.api.routes.users import router as users_router
from src.api.routes.auth import router as auth_router
from src.api.routes.comments import router as comments_router
from src.api.routes.comments_actions import router as comments_actions_router
from src.api.routes.categories import router as categories_router
from src.core.config import settings
from src.core.exceptions import (
    DatabaseError,
    UserAlreadyExistsError,
    NotFoundError,
    ForbiddenError,
)
from src.core.logging import configure_logging
from src.api.middleware.logging import logging_middleware
from src.db.db import database

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    configure_logging()
    app = FastAPI(root_path="/api/v1")

    app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.mount("/static", StaticFiles(directory="static"), name="static")

    app.middleware("http")(logging_middleware)

    authentication_backend = AdminAuthBackend(secret_key=settings.SECRET_KEY)
    admin = Admin(
        app,
        database._engine,
        authentication_backend=authentication_backend,
        base_url="/admin",
    )
    admin.add_view(UserAdmin)
    admin.add_view(PostAdmin)
    admin.add_view(CommentAdmin)
    admin.add_view(CategoryAdmin)
    admin.add_view(LocationAdmin)

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        logger.exception(f"Unhandled exception: {exc}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": "Internal server error."},
        )

    @app.exception_handler(DatabaseError)
    async def database_error_handler(request: Request, exc: DatabaseError):
        logger.error(f"Database error: {exc}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": "Database error occurred."},
        )

    @app.exception_handler(UserAlreadyExistsError)
    async def user_already_exists_handler(
        request: Request, exc: UserAlreadyExistsError
    ):
        logger.warning(f"User already exists: {exc.message}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": exc.message},
        )

    @app.exception_handler(NotFoundError)
    async def not_found_error_handler(request: Request, exc: NotFoundError):
        logger.info(f"Not found error: {exc.message}")
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": exc.message},
        )

    @app.exception_handler(ForbiddenError)
    async def forbidden_error_handler(request: Request, exc: ForbiddenError):
        logger.warning(f"Forbidden error: {exc.message}")
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"message": exc.message},
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ):
        errors = []
        for error in exc.errors():
            field = ".".join(str(loc) for loc in error["loc"])
            message = error["msg"]
            errors.append(f"{field}: {message}")
        logger.warning(f"Validation error: {errors}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": errors},
        )

    app.include_router(users_router, prefix="/users", tags=["User APIs"])
    app.include_router(posts_router, prefix="/posts", tags=["Post APIs"])
    app.include_router(categories_router, prefix="/categories", tags=["Category APIs"])
    app.include_router(
        comments_router, prefix="/posts/{post_id}/comments", tags=["Comment APIs"]
    )
    app.include_router(
        comments_actions_router, prefix="/comments", tags=["Comment APIs"]
    )
    app.include_router(auth_router, prefix="/auth", tags=["Auth APIs"])

    @app.get("/health")
    async def health_check():
        return {"status": "ok"}

    return app
