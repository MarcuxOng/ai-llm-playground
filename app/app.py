from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.db import Base, engine
from app.routers import all_routers


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(
    title="AI/LLM Playground",
    description="",
    version="1.0.0",
    lifespan=lifespan
)


for router in all_routers:
    app.include_router(router)


@app.get("/")
async def root():
    return {"message": "App is running"}