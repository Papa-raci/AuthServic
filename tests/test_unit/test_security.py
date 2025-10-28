import pytest
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.core.config import settings
from app.core.exceptions import InvalidToken


def test_hash_and_verify_password():
    """Тестирует хеширование и проверку пароля."""
    password = "My$trongPassw0rd!"
    hashed = hash_password(password)

    assert hashed != password
    assert isinstance(hashed, str)
    assert verify_password(password, hashed)
    assert not verify_password("WrongPa$$word", hashed)


def test_create_and_decode_tokens():
    """Тестирует создание и декодирование access и refresh токенов."""
    data = {"sub": "test@example.com"}

    access_token = create_access_token(data)
    payload_access = decode_token(access_token)
    assert payload_access["sub"] == data["sub"]
    assert "exp" in payload_access

    refresh_token = create_refresh_token(data)
    payload_refresh = decode_token(refresh_token)
    assert payload_refresh["sub"] == data["sub"]
    assert "exp" in payload_refresh

    assert payload_access["exp"] < payload_refresh["exp"]


def test_decode_invalid_token():
    """Тестирует декодирование невалидного токена."""
    with pytest.raises(InvalidToken, match="Недействительный токен"):
        decode_token("not.a.real.token")


def test_decode_expired_token(monkeypatch):
    """Тестирует декодирование просроченного токена."""
    monkeypatch.setattr(settings, "ACCESS_TOKEN_EXPIRE_MINUTES", -1)
    
    expired_token = create_access_token({"sub": "test"})
    
    with pytest.raises(InvalidToken, match="Токен истек"):
        decode_token(expired_token)