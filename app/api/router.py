from fastapi import APIRouter

from app.api.routes.auth import router as auth_router
from app.api.routes.pages import router as pages_router
from app.api.routes.study import router as study_router


api_router = APIRouter()
api_router.include_router(pages_router)
api_router.include_router(auth_router, prefix="/api/auth", tags=["auth"])
api_router.include_router(study_router, prefix="/api/study", tags=["study"])
