import logging
from fastapi import APIRouter

from app.agents import PRESETS

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/agents", tags=["Agents"])


@router.get("/")
async def get_presets():
    """List available agent presets."""
    return {"presets": list(PRESETS.keys())}