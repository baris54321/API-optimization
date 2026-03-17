from contextlib import asynccontextmanager

from fastapi import FastAPI

from database import engine
from routers.users import router as users_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await engine.dispose()


app = FastAPI(
    title="API Optimization - FastAPI",
    description="FastAPI application connected to the same PostgreSQL database",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(users_router)


@app.get("/")
async def root():
    return {"message": "FastAPI is running", "docs": "/docs"}
