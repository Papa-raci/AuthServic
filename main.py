from fastapi import FastAPI
from contextlib import asynccontextmanager
from api import auth
from db.database import connect_to_db, close_db_connection

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_db()
    yield
    await close_db_connection()

app = FastAPI(lifespan=lifespan)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])