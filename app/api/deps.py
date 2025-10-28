from fastapi import Depends
from app.db.database import get_db_pool
from app.db.repository import UserRepository
from app.services.auth_service import AuthService

def get_user_repository() -> UserRepository:
    """Зависимость, которая предоставляет экземпляр UserRepository."""
    pool = get_db_pool()
    return UserRepository(pool)

def get_auth_service(
    repo: UserRepository = Depends(get_user_repository)
) -> AuthService:
    """Зависимость, которая предоставляет экземпляр AuthService."""
    return AuthService(user_repo=repo)