from unittest.mock import patch
import pytest
from app.core.exceptions import UserAlreadyExists, InvalidCredentials, InvalidToken
from app.core.security import create_access_token, create_refresh_token

@pytest.mark.asyncio
class TestAuthService:
    """Группировка тестов сервиса"""

    async def test_register_user_success(self, auth_service, mock_user_repo, sample_user_data):
        """Тест успешной регистрации нового пользователя."""    
        mock_user_repo.get_user_by_email.return_value = None
        mock_user_repo.create_user.return_value = {"email": sample_user_data["email"]}

        with patch('app.services.auth_service.hash_password') as mock_hash:
            mock_hash.return_value = "hashed_password"
            user = await auth_service.register_user(sample_user_data["email"], sample_user_data["password"])

        assert user["email"] == sample_user_data["email"]
        mock_user_repo.get_user_by_email.assert_called_with(sample_user_data["email"])
        mock_user_repo.create_user.assert_called_with(sample_user_data["email"], "hashed_password")


    async def test_register_user_already_exists(self, auth_service, mock_user_repo, sample_user_data, sample_user_db):
        """Тест регистрации, когда email уже занят."""
        
        mock_user_repo.get_user_by_email.return_value = sample_user_db
        with pytest.raises(UserAlreadyExists, match="уже существует"):
            await auth_service.register_user(sample_user_data["email"], sample_user_data["password"])
        
        mock_user_repo.get_user_by_email.assert_called_with(sample_user_data["email"])
        mock_user_repo.create_user.assert_not_called()


    async def test_login_user_success(self, auth_service, mock_user_repo, sample_user_data, sample_user_db):
        """Тест успешного входа."""
        mock_user_repo.get_user_by_email.return_value = sample_user_db

        with patch('app.services.auth_service.verify_password') as mock_verify:
            mock_verify.return_value = True
            tokens = await auth_service.login_user(sample_user_data["email"], sample_user_data["password"])
        
        assert "access_token" in tokens


    async def test_login_user_not_found(self, auth_service, mock_user_repo, sample_user_data):
        """Тест входа с неверным email."""
        mock_user_repo.get_user_by_email.return_value = None

        with pytest.raises(InvalidCredentials, match="Неверный email или пароль"):
            await auth_service.login_user(sample_user_data["email"], sample_user_data["password"])


    async def test_login_user_wrong_password(self, auth_service, mock_user_repo, sample_user_data, sample_user_db):
        """Тест входа с неверным паролем."""    
        mock_user_repo.get_user_by_email.return_value = sample_user_db

        with patch('app.services.auth_service.verify_password') as mock_verify:
            mock_verify.return_value = False
            with pytest.raises(InvalidCredentials, match="Неверный email или пароль"):
                await auth_service.login_user(sample_user_data["email"], "wrong_password")

    async def test_refresh_tokens_success(self, auth_service, mock_user_repo, sample_user_data, sample_user_db):
        """Тест успешного обновления токенов."""
        refresh_token = create_refresh_token({"sub": sample_user_data["email"]})
        mock_user_repo.get_user_by_email.return_value = sample_user_db

        tokens = await auth_service.refresh_tokens(refresh_token)

        assert "access_token" in tokens
        assert "refresh_token" in tokens
        mock_user_repo.get_user_by_email.assert_called_with(sample_user_data["email"])


    async def test_refresh_tokens_invalid(self, auth_service):
        """Тест обновления с невалидным токеном."""
        with pytest.raises(InvalidToken):
            await auth_service.refresh_tokens("invalid.token.string")


    async def test_refresh_tokens_user_not_found(self, auth_service, mock_user_repo, sample_user_data):
        """Тест обновления, когда пользователь из токена удален."""
        refresh_token = create_refresh_token({"sub": sample_user_data["email"]})
        mock_user_repo.get_user_by_email.return_value = None

        with pytest.raises(InvalidToken, match="Пользователь из токена не найден"):
            await auth_service.refresh_tokens(refresh_token)


    async def test_get_user_from_token_success(self, auth_service, mock_user_repo, sample_user_data, sample_user_db):
        """Тест получения пользователя по access-токену."""
        access_token = create_access_token({"sub": sample_user_data["email"]})
        mock_user_repo.get_user_by_email.return_value = sample_user_db

        user = await auth_service.get_user_from_token(access_token)
        
        assert user == sample_user_db
        mock_user_repo.get_user_by_email.assert_called_with(sample_user_data["email"])