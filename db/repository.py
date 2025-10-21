import asyncmy
from asyncmy.cursors import DictCursor

class UserRepository:
    def __init__(self, pool: asyncmy.Pool):
        self.pool = pool

    async def create_user(self, email: str, hashed_password: str) -> dict | None:
        query = "INSERT INTO users (email, hashed_password) VALUES (%s, %s)"
        try:
            async with self.pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(query, (email, hashed_password))
            return {"email": email}
        except asyncmy.errors.IntegrityError:
            return None
        
    async def get_user_by_email(self, email: str) -> dict | None:
        query = "SELECT * FROM users WHERE email = %s"
        async with self.pool.acquire() as conn:
            async with conn.cursor(DictCursor) as cursor:
                await cursor.execute(query, (email,))
                user = await cursor.fetchone()
                return user