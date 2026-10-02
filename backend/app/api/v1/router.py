from fastapi import APIRouter
from app.api.v1.endpoints.notifications import router as notifications_router
from app.api.v1.endpoints.tenants import router as tenants_router

api_v1_router = APIRouter(prefix="/v1")
api_v1_router.include_router(notifications_router)
api_v1_router.include_router(tenants_router)
