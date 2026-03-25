import os
import uvicorn

from app.app import app

def main():
    # Use the PORT environment variable if available, otherwise default to 8000 for local development.
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "app.app:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        log_level="info",
    )