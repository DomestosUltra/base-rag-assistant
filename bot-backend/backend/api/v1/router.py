from fastapi import APIRouter

from backend.api.v1.routers.health import router as health_router
from backend.api.v1.routers.knowledge import router as knowledge_router
from backend.api.v1.routers.query import router as query_router

router = APIRouter(prefix="/v1")
router.include_router(health_router)
router.include_router(knowledge_router)
router.include_router(query_router)
