from app.routers.providers import router as providers_router
from app.routers.models import router as models_router

all_routers = [
    providers_router,
    models_router,
]