from fastapi import FastAPI

from app.routers import all_routers

app = FastAPI(
    title="AI & LLM Playground",
    description="",
    version="1.0.0"
)


for router in all_routers:
    app.include_router(router)


@app.get("/")
async def root():
    return {"message": "App is running"}