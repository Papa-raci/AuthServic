from fastapi import APIRouter, Depends, HTTPException, status
from app.api.deps import get_auth_service
from app.core.exceptions import InvalidCredentials, InvalidToken, UserAlreadyExists
from app.schemas.user import MessageResponse, RefreshTokenRequest, TokenResponse, UserCreate
from fastapi.security import OAuth2PasswordRequestForm
from app.services.auth_service import AuthService

router = APIRouter()

@router.post("/sign-up", response_model=MessageResponse)
async def sign_up(
    user_in: UserCreate,
    auth_service: AuthService = Depends(get_auth_service)  
):
    try:
        await auth_service.register_user(
            email=user_in.email, password=user_in.password
        )
    except UserAlreadyExists as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    return MessageResponse(message="Пользователь успешно зарегистрирован")

@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service)
):
    try:
        tokens = await auth_service.login_user(
            email=form_data.username, password=form_data.password
        )
    except InvalidCredentials as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    return tokens

@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    token_in: RefreshTokenRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    try:
        tokens = await auth_service.refresh_tokens(token_in.refresh_token)
    except InvalidToken as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        ) 
    return tokens
    