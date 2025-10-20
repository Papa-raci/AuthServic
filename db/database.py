import asyncmy
from core.config import settings

pool: asyncmy.Pool = None

async def connect_to_db():
    global pool
    pool = await asyncmy.create_pool(
        host=settings.DATABASE_HOST, port=settings.DATABASE_PORT,
        user=settings.DATABASE_USER, password=settings.DATABASE_PASSWORD,
        db=settings.DATABASE_NAME, autocommit=True
    )
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    hashed_password VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

async def close_db_connection():
    pool.close()
    await pool.wait_closed()

def get_db_pool() -> asyncmy.Pool:
    return pool