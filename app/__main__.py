import uvicorn
from dotenv import load_dotenv
from app.app import app

load_dotenv()

if __name__ == '__main__':
    uvicorn.run(
        "app.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )