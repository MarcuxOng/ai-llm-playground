from app.routers.providers import router as providers_router
from app.routers.models import router as models_router
from app.routers.agents import router as agents_router

all_routers = [
    models_router,
    providers_router,
    agents_router,
]