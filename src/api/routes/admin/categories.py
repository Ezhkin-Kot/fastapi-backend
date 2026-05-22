import uuid

from fastapi import APIRouter, Depends

from src.api.dependencies import (
    create_category_use_case,
    update_category_use_case,
    delete_category_use_case,
)
from src.domain.category.use_cases.create_category import CreateCategoryUseCase
from src.domain.category.use_cases.update_category import UpdateCategoryUseCase
from src.domain.category.use_cases.delete_category import DeleteCategoryUseCase
from src.schemas.categories import CategoryResponse, CategoryCreate, CategoryUpdate
from src.services.auth import get_current_admin_user

router = APIRouter(dependencies=[Depends(get_current_admin_user)])


@router.post("/", response_model=CategoryResponse, status_code=201)
async def create_category(
    category_in: CategoryCreate,
    use_case: CreateCategoryUseCase = Depends(create_category_use_case),
):
    category = await use_case.execute(category_in)
    return CategoryResponse.model_validate(category)


@router.put(
    "/{category_id}",
    response_model=CategoryResponse,
)
async def update_category(
    category_id: uuid.UUID,
    category_in: CategoryUpdate,
    use_case: UpdateCategoryUseCase = Depends(update_category_use_case),
):
    category = await use_case.execute(category_id, category_in)
    return CategoryResponse.model_validate(category)


@router.delete("/{category_id}", status_code=204)
async def delete_category(
    category_id: uuid.UUID,
    use_case: DeleteCategoryUseCase = Depends(delete_category_use_case),
):
    await use_case.execute(category_id)
    return
