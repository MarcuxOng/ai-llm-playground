from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException

from app.db import Base, engine
from app.routers import all_routers
from app.utils.exceptions import http_exception_handler, unhandled_exception_handler
from app.utils.logging import setup_logging

# Setup logging before FastAPI instance
setup_logging()

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

# Register custom exception handlers
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)


for router in all_routers:
    app.include_router(router)


@app.get("/api/v1/health")
async def health():
    return {"message": "Health check passed"}


@app.get("/")
async def root():
    return {"message": "App is running"}