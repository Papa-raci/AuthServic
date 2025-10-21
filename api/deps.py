from db.database import get_db_pool
from db.repository import UserRepository

def get_user_repository() -> UserRepository:
    """Зависимость, которая предоставляет экземпляр UserRepository."""
    pool = get_db_pool()
    return UserRepository(pool)