from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from core.exceptions import InvalidToken
from services.auth_service import AuthService
from .deps import get_auth_service

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service),
):
    try:
        user = await auth_service.get_user_from_token(token)
    except InvalidToken as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    return user
    
@router.get("/secret-data")
async def get_secret_data(current_user: dict = Depends(get_current_user)):
    return {"message": f"Это секретные данные для {current_user['email']}"}