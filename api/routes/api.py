# app/api/routes/api.py

from fastapi import APIRouter

from api.routes import predictor
from api.routes_sych import router as sych_router  # ✅ import correct

router = APIRouter()
router.include_router(predictor.router, tags=["predictor"], prefix="/v1")
router.include_router(sych_router, tags=["synchronisation"], prefix="/v1")
