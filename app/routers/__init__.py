from app.routers.auth import router as auth_router
from app.routers.threads import router as threads_router
from app.routers.agents import router as agents_router
from app.routers.rag import router as rag_router
from app.routers.gemini import router as gemini_router
# from app.routers.groq import router as groq_router
# from app.routers.mistral import router as mistral_router
# from app.routers.openrouter import router as openrouter_router

all_routers = [
    auth_router,
    threads_router,
    agents_router,
    rag_router,
    gemini_router,
    # groq_router,
    # mistral_router,
    # openrouter_router,
]