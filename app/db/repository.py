import asyncpg

class UserRepository:
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def create_user(self, email: str, hashed_password: str) -> dict | None:
        query = "INSERT INTO users (email, hashed_password) VALUES ($1, $2) RETURNING id, email"
        try:
            async with self.pool.acquire() as conn:
                user = await conn.fetchrow(query, email, hashed_password)
                return dict(user) if user else None
        except asyncpg.UniqueViolationError:
            return None
        
    async def get_user_by_email(self, email: str) -> dict | None:
        query = "SELECT * FROM users WHERE email = $1"
        async with self.pool.acquire() as conn:
            user = await conn.fetchrow(query, email)
            return dict(user) if user else None