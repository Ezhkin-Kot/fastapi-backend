from fastapi import APIRouter

from src.api.routes.admin import categories

router = APIRouter()

router.include_router(
    categories.router,
    prefix="/categories",
    tags=["Admin-Categories"],
)
