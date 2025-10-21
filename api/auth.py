from fastapi import APIRouter, Depends, HTTPException, status
from schemas.user import RefreshTokenRequest, TokenResponse, UserCreate
from core.security import create_access_token, create_refresh_token, decode_token, hash_password, verify_password
from db.repository import UserRepository
from fastapi.security import OAuth2PasswordRequestForm
from .deps import get_user_repository

router = APIRouter()

@router.post("/sign-up", status_code=status.HTTP_201_CREATED)
async def sign_up(user_in: UserCreate, repo: UserRepository = Depends(get_user_repository)):
    hashed_pwd = hash_password(user_in.password)
    user = await repo.create_user(user_in.email, hashed_pwd)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует"
        )
    return {"message": "Пользователь успешно зарегистрирован"}

@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    repo: UserRepository = Depends(get_user_repository)
):
    user = await repo.get_user_by_email(form_data.username)

    if not user or not verify_password(form_data.password, user['hashed_password']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль"
        )
    
    access_token = create_access_token(data={"sub": user['email']})
    refresh_token = create_refresh_token(data={"sub": user['email']})
    return {"access_token": access_token, "refresh_token": refresh_token}

@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    token_in: RefreshTokenRequest,
    repo: UserRepository = Depends(get_user_repository)
):
    payload = decode_token(token_in.refresh_token)
    if not payload or not payload.get("sub"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительный refresh токен"
        )
    user = await repo.get_user_by_email(payload["sub"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден"
        )
    access_token = create_access_token(data={"sub": user['email']})
    refresh_token = create_refresh_token(data={"sub": user['email']})   
    return {"access_token": access_token, "refresh_token": refresh_token}
    