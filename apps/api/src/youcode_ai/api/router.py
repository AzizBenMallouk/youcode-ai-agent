from fastapi import APIRouter

from youcode_ai.api.routes.chat import (
    router as chat_router,
)
from youcode_ai.api.routes.support_requests import (
    router as support_requests_router,
)
from youcode_ai.api.routes.newsletter import (
    router as newsletter_router,
)
from youcode_ai.api.routes.admin_newsletter import (
    router as admin_newsletter_router,
)
from youcode_ai.api.routes.auth import (
    router as auth_router,
)
from youcode_ai.api.routes.admin_users import (
    router as admin_users_router,
)


api_router = APIRouter(
    prefix="/api/v1"
)


api_router.include_router(
    chat_router
)
api_router.include_router(
    support_requests_router
)
api_router.include_router(
    auth_router
)
api_router.include_router(
    admin_users_router
)
api_router.include_router(
    newsletter_router
)
api_router.include_router(
    admin_newsletter_router
)