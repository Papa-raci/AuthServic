from typing import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock
import asyncpg
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from fastapi import FastAPI

from app.core.config import settings
from app.db import database
from app.db.database import get_db_pool
from app.db.repository import UserRepository
from app.main import app
from app.services.auth_service import AuthService

TEST_DB_NAME = "test_auth_db"
ROOT_USER = "app_user"
ROOT_PASSWORD = "app_password"


@pytest_asyncio.fixture(scope="session")
async def setup_test_db():
    """Создает тестовую БД перед всеми тестами и удаляет после."""
    conn = await asyncpg.connect(
        host=settings.DATABASE_HOST,
        port=settings.DATABASE_PORT,
        user=ROOT_USER,
        password=ROOT_PASSWORD,
        database="postgres"
    )

    await conn.execute(f"DROP DATABASE IF EXISTS {TEST_DB_NAME}")
    await conn.execute(f"CREATE DATABASE {TEST_DB_NAME}")
    await conn.close()
    
    yield

    conn = await asyncpg.connect(
        host=settings.DATABASE_HOST,
        port=settings.DATABASE_PORT,
        user=ROOT_USER,
        password=ROOT_PASSWORD,
        database="postgres"
    )
    await conn.execute(f"DROP DATABASE IF EXISTS {TEST_DB_NAME}")
    await conn.close()


@pytest_asyncio.fixture
async def test_db_pool(setup_test_db) -> AsyncGenerator[asyncpg.Pool, None]:
    """Создает пул соединений и накатывает схему перед каждым тестом (scope='function' по умолчанию)."""
    pool = await asyncpg.create_pool(
        host=settings.DATABASE_HOST,
        port=settings.DATABASE_PORT,
        user=settings.DATABASE_USER,
        password=settings.DATABASE_PASSWORD,
        database=TEST_DB_NAME
    )

    async with pool.acquire() as conn:
            await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                hashed_password VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

    database.pool = pool
    
    yield pool

    async with pool.acquire() as conn:
        await conn.execute("TRUNCATE TABLE users RESTART IDENTITY CASCADE")

    await pool.close()


@pytest_asyncio.fixture
async def test_app(test_db_pool: asyncpg.Pool) -> FastAPI:
    """Создает приложение FastAPI, использующее тестовую БД."""
    async def override_get_db_pool():
        return test_db_pool

    app.dependency_overrides[get_db_pool] = override_get_db_pool
    return app


@pytest_asyncio.fixture
async def client(test_app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """HTTP-клиент для интеграционных тестов."""
    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def mock_user_repo() -> MagicMock:
    repo = MagicMock(spec=UserRepository)
    repo.get_user_by_email = AsyncMock()
    repo.create_user = AsyncMock()
    return repo


@pytest.fixture
def auth_service(mock_user_repo: MagicMock) -> AuthService:
    return AuthService(user_repo=mock_user_repo)


@pytest.fixture
def sample_user_data():
    return {
        "email": "test@example.com",
        "password": "password123",
        "password_confirm": "password123"
    }


@pytest.fixture
def sample_user_db():
    return {
        "id": 1,
        "email": "test@example.com", 
        "hashed_password": "$2b$12$hashed_password",
        "created_at": "2023-01-01 00:00:00"
    }


@pytest.fixture
async def registered_user(client, sample_user_data):
    """Фикстура для уже зарегистрированного пользователя"""
    await client.post("/api/v1/auth/sign-up", json=sample_user_data)
    return sample_user_data.copy()


@pytest.fixture  
async def authenticated_user(client, registered_user):
    """Фикстура для аутентифицированного пользователя с токенами"""
    login_response = await client.post(
        "/api/v1/auth/login",
        data={"username": registered_user["email"], "password": registered_user["password"]}
    )
    tokens = login_response.json()
    return registered_user, tokens