from fastapi import APIRouter
from youcode_ai.api.routes.auth import (
    router as auth_router,
)
from youcode_ai.api.routes.newsletter import (
    router as newsletter_router,
)
from youcode_ai.api.routes.support_requests import (
    router as support_requests_router,
)
from youcode_ai.api.routes.whatsapp import (
    router as whatsapp_router,
)

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(support_requests_router)
api_router.include_router(auth_router)
api_router.include_router(newsletter_router)
api_router.include_router(whatsapp_router)
