from fastapi import FastAPI

app = FastAPI(
    title="AI & LLM Playground",
    description="",
    version="1.0.0"
)

@app.get("/")
async def root():
    return {"message": "App is running"}