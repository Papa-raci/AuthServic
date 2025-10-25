class AuthError(Exception):
    """Базовый класс для ошибок аутентификации."""
    pass

class UserAlreadyExists(AuthError):
    """Вызывается, если пользователь с таким email уже существует."""
    pass

class InvalidCredentials(AuthError):
    """Вызывается при неверном логине или пароле."""
    pass

class InvalidToken(AuthError):
    """Вызывается, если токен невалиден, просрочен или не найден."""
    pass