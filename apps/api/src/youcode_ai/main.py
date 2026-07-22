from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from youcode_ai.api.router import api_router
from youcode_ai.core.config import settings


@asynccontextmanager
async def lifespan(
    application: FastAPI,
) -> AsyncIterator[None]:

    yield


def create_application() -> FastAPI:
    application = FastAPI(
        title=settings.app_name,
        debug=settings.app_debug,
        version="0.1.0",
        lifespan=lifespan,
    )

    application.include_router(
        api_router
    )

    return application


app = create_application()