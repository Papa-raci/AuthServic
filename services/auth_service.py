from core.exceptions import InvalidCredentials, InvalidToken, UserAlreadyExists
from core.security import create_access_token, create_refresh_token, decode_token, hash_password, verify_password
from db.repository import UserRepository


class AuthService:
    """Сервис для аутентификации пользователей."""
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def register_user(self, email: str, password: str) -> dict:
        """Регистрация нового пользователя."""
        existing_user = await self.user_repo.get_user_by_email(email)
        if existing_user:
            raise UserAlreadyExists("Пользователь с таким email уже существует")
        
        hashed_pwd = hash_password(password)
        user = await self.user_repo.create_user(email, hashed_pwd)
        return user
    
    async def login_user(self, email: str, password: str) -> dict:
        """Аутентификация пользователя."""
        user = await self.user_repo.get_user_by_email(email)
        if not user and not verify_password(password, user['hashed_password']):
            raise InvalidCredentials("Неверный email или пароль")
        
        access_token = create_access_token(data={"sub": user['email']})
        refresh_token = create_refresh_token(data={"sub": user['email']})
        return {"access_token": access_token, "refresh_token": refresh_token}
    
    async def refresh_tokens(self, refresh_token: str) -> dict:
        """Обновление токенов доступа"""
        payload = decode_token(refresh_token)
        if not payload or not payload.get("sub"):
            raise InvalidToken("Недействительный refresh токен")
        
        email = payload["sub"]
        user = await self.user_repo.get_user_by_email(email)
        if not user:
            raise InvalidToken("Пользователь из токена не найден")
        
        new_access_token = create_access_token(data={"sub": user['email']})
        new_refresh_token = create_refresh_token(data={"sub": user['email']})
        return {"access_token": new_access_token, "refresh_token": new_refresh_token}
    
    async def get_user_from_token(self, token: str) -> dict:
        """Получение пользователя по токену."""
        payload = decode_token(token)
        if not payload or not payload.get("sub"):
            raise InvalidToken("Недействительный access-токен")
        
        email = payload["sub"]
        user = await self.user_repo.get_user_by_email(email)
        if not user:
            raise InvalidToken("Пользователь из токена не найден")
        
        return user