from fastapi import APIRouter
from .hosts import router as hosts_router
from .services import router as services_router
from .updates import router as updates_router
from .dashboard import router as dashboard_router
from .alerts import router as alerts_router
from .jobs import router as jobs_router
from .websocket import router as ws_router

api_router = APIRouter()
api_router.include_router(hosts_router, prefix="/hosts", tags=["hosts"])
api_router.include_router(services_router, prefix="/services", tags=["services"])
api_router.include_router(updates_router, prefix="/updates", tags=["updates"])
api_router.include_router(dashboard_router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(alerts_router, prefix="/alerts", tags=["alerts"])
api_router.include_router(jobs_router, prefix="/jobs", tags=["jobs"])
api_router.include_router(ws_router, tags=["websocket"])
