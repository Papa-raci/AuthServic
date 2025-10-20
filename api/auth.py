from fastapi import APIRouter, Depends, HTTPException, status
from schemas.user import UserCreate
from core.security import hash_password
from db.database import get_db_pool
from db.repository import UserRepository
import asyncmy

router = APIRouter()

@router.post("/sign-up", status_code=status.HTTP_201_CREATED)
async def sign_up(user_in: UserCreate, pool: asyncmy.Pool = Depends(get_db_pool)):
    repo = UserRepository(pool)
    hashed_pwd = hash_password(user_in.password)
    user = await repo.create_user(user_in.email, hashed_pwd)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    return {"message": "User created successfully"}