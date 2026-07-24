from __future__ import annotations

import logging
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from youcode_ai.api.dependencies.database import get_database_session
from youcode_ai.core.config import settings
from youcode_ai.infrastructure.database.repositories.user import UserRepository
from youcode_ai.infrastructure.database.tables.user import UserTable
from youcode_ai.infrastructure.security.tokens import decode_access_token

logger = logging.getLogger(__name__)


def get_current_user(
    request: Request,
    session: Annotated[Session, Depends(get_database_session)],
) -> UserTable:
    # Try cookie first, then Authorization header
    token = request.cookies.get("access_token")
    if not token:
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
        )

    try:
        payload = decode_access_token(token, secret_key=settings.auth_secret_key)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired.",
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token.",
        )

    user_repo = UserRepository(session=session)
    user = user_repo.get_by_id(payload["sub"])

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account not found or disabled.",
        )

    return user


CurrentUser = Annotated[UserTable, Depends(get_current_user)]


def require_roles(*allowed_roles: str):
    def dependency(current_user: CurrentUser) -> UserTable:
        if current_user.role.value not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions.",
            )
        return current_user

    return dependency
