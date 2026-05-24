from fastapi import APIRouter, Depends, HTTPException, status, Form, Header
from fastapi.security import OAuth2PasswordRequestForm

from src.api.dependencies import (
    authenticate_user_use_case,
    refresh_token_use_case,
    logout_user_use_case,
)
from src.domain.auth.use_cases.authenticate_user import AuthenticateUserUseCase
from src.domain.auth.use_cases.refresh_token import RefreshTokenUseCase
from src.domain.auth.use_cases.logout_user import LogoutUserUseCase
from src.services.auth import Token, get_current_user
from src.db.models.users import User
from src.resources.auth import oauth2_scheme

router = APIRouter()


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_use_case: AuthenticateUserUseCase = Depends(authenticate_user_use_case),
):
    token_data = await auth_use_case.execute(form_data.username, form_data.password)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token_data


@router.post("/refresh", response_model=Token)
async def refresh_access_token(
    refresh_token: str = Form(...),
    refresh_use_case: RefreshTokenUseCase = Depends(refresh_token_use_case),
):
    try:
        new_tokens = await refresh_use_case.execute(refresh_token)
        return new_tokens
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/logout")
async def logout_user(
    current_user: User = Depends(get_current_user),
    token: str = Depends(oauth2_scheme),
    refresh_token: str | None = Header(default=None, alias="X-Refresh-Token"),
    logout_use_case: LogoutUserUseCase = Depends(logout_user_use_case),
):
    await logout_use_case.execute(token, refresh_token)
    return {"message": "Logged out successfully"}
