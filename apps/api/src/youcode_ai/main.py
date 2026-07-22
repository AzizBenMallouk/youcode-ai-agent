import logging
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import (
    CORSMiddleware,
)

from youcode_ai.api.router import (
    api_router,
)
from youcode_ai.core.config import (
    settings,
)
from youcode_ai.infrastructure.database import (
    initialize_database,
)


logging.basicConfig(
    level=(
        logging.DEBUG
        if settings.app_debug
        else logging.INFO
    ),
    format=(
        "%(asctime)s | %(levelname)s | "
        "%(name)s | %(message)s"
    ),
)


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(
    app: FastAPI,
) -> AsyncIterator[None]:
    """
    Initialise les ressources nécessaires au
    démarrage de l'API.
    """

    logger.info(
        "Starting %s.",
        settings.app_name,
    )

    initialize_database()

    yield

    logger.info(
        "Stopping %s.",
        settings.app_name,
    )


app = FastAPI(
    title=settings.app_name,
    description=(
        "API multi-agent de YouCode pour les "
        "visiteurs, candidats et administrateurs."
    ),
    version="0.1.0",
    debug=settings.app_debug,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=[
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
        "OPTIONS",
    ],
    allow_headers=[
        "Authorization",
        "Content-Type",
    ],
)


app.include_router(
    api_router
)

from fastapi import Request
from fastapi.responses import JSONResponse
from youcode_ai.domain.exceptions import (
    DomainError,
    AuthenticationError,
    AuthorizationError,
    AccountLockedError,
    AccountDisabledError,
    DuplicateEmailError,
)

@app.exception_handler(DomainError)
async def domain_error_handler(request: Request, exc: DomainError):
    status_code = 400
    
    if isinstance(exc, AuthenticationError):
        status_code = 401
    elif isinstance(exc, (AuthorizationError, AccountDisabledError, AccountLockedError)):
        status_code = 403
    elif isinstance(exc, DuplicateEmailError):
        status_code = 409
        
    return JSONResponse(
        status_code=status_code,
        content={"detail": str(exc)},
    )


@app.get(
    "/health",
    tags=["Health"],
)
def health_check() -> dict[str, str]:
    return {
        "status": "healthy",
        "application": settings.app_name,
        "environment": settings.app_env,
    }