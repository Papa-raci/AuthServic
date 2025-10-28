import pytest

@pytest.mark.asyncio
class TestAuthAPI:
    
    
    async def test_sign_up_success(self, client, sample_user_data):
        """Тест успешной регистрации."""
        response = await client.post("/api/v1/auth/sign-up", json=sample_user_data)
        assert response.status_code == 200
        assert response.json() == {"message": "Пользователь успешно зарегистрирован"}


    async def test_sign_up_password_mismatch(self, client, sample_user_data):
        """Тест регистрации с несовпадающими паролями (ошибка Pydantic 422)."""
        invalid_data = sample_user_data.copy()
        invalid_data["password_confirm"] = "different_password"
        
        response = await client.post("/api/v1/auth/sign-up", json=invalid_data)
        assert response.status_code == 422
        assert any("Пароли не совпадают" in err["msg"] for err in response.json().get("detail", []))


    async def test_sign_up_user_already_exists(self, client, registered_user, sample_user_data):
        """Тест регистрации с email, который уже занят (ошибка 400)."""
        response = await client.post("/api/v1/auth/sign-up", json=sample_user_data)
        assert response.status_code == 400
        assert "Пользователь с таким email уже существует" in response.json()["detail"]


    async def test_login_success(self, client, registered_user):
        """Тест успешного входа."""
        login_response = await client.post(
            "/api/v1/auth/login", 
            data={"username": registered_user["email"], "password": registered_user["password"]}
        )
        assert login_response.status_code == 200
        tokens = login_response.json()
        assert "access_token" in tokens
        assert "refresh_token" in tokens
    

    async def test_protected_route_with_token(self, client, authenticated_user):
        """Тест доступа к защищенному роуту с валидным токеном."""
        user_data, tokens = authenticated_user
        
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        secret_response = await client.get("/api/v1/protected-scv/secret-data", headers=headers)
        
        assert secret_response.status_code == 200
        assert secret_response.json() == {
            "message": f"Это секретные данные для пользователя {user_data['email']}"
        }


    async def test_refresh_tokens_success(self, client, authenticated_user):
        """Тест успешного обновления токенов."""
        tokens = authenticated_user[1]
        
        refresh_response = await client.post(
            "/api/v1/auth/refresh", 
            json={"refresh_token": tokens["refresh_token"]}
        )
        assert refresh_response.status_code == 200
        new_tokens = refresh_response.json()
        assert "access_token" in new_tokens
        assert "refresh_token" in new_tokens
        assert new_tokens["access_token"] != tokens["access_token"]


    async def test_login_invalid_credentials(self, client, registered_user):
        """Тест входа с неверным паролем (ошибка 401)."""
        response = await client.post(
            "/api/v1/auth/login",
            data={"username": registered_user["email"], "password": "wrong_password"},
        )
        assert response.status_code == 401
        assert "Неверный email или пароль" in response.json()["detail"]


    async def test_protected_route_no_token(self, client):
        """Тест доступа к защищенному роуту без токена (ошибка 401)."""
        response = await client.get("/api/v1/protected-scv/secret-data")
        assert response.status_code == 401
        assert response.json() == {"detail": "Not authenticated"}


    async def test_protected_route_invalid_token(self, client):
        """Тест доступа к защищенному роуту с невалидным токеном."""
        headers = {"Authorization": "Bearer invalid.jwt.token"}
        response = await client.get("/api/v1/protected-scv/secret-data", headers=headers)
        assert response.status_code == 401
        assert "Недействительный токен" in response.json()["detail"]
