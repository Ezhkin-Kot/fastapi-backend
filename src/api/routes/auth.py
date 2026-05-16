from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from src.api.dependencies import (
    authenticate_user_use_case,
    create_access_token_use_case,
)
from src.domain.auth.use_cases.authenticate_user import AuthenticateUserUseCase
from src.domain.auth.use_cases.create_access_token import CreateAccessTokenUseCase
from src.services.auth import Token

router = APIRouter()


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_use_case: AuthenticateUserUseCase = Depends(authenticate_user_use_case),
    token_use_case: CreateAccessTokenUseCase = Depends(create_access_token_use_case),
):
    user = await auth_use_case.execute(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = token_use_case.execute(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}
