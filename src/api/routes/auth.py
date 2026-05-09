from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from core.db import get_async_session
from domain.auth.use_cases.authenticate_user import AuthenticateUserUseCase
from domain.auth.use_cases.create_access_token import CreateAccessTokenUseCase
from services.auth import Token

router = APIRouter()


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_async_session),
):
    auth_use_case = AuthenticateUserUseCase(session)
    user = await auth_use_case.execute(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token_use_case = CreateAccessTokenUseCase()
    access_token = token_use_case.execute(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}
