from fastapi import APIRouter, Depends, Request, Response, status
from youcode_ai.api.dependencies.database import DatabaseSession
from youcode_ai.api.dependencies.auth import CurrentUser
from youcode_ai.application.services.factories import create_auth_service
from youcode_ai.api.schemas.auth import LoginRequest, TokenResponse, UserResponse
from youcode_ai.core.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, response: Response, session: DatabaseSession):
    auth_service = create_auth_service(session=session)
    tokens = auth_service.login(
        email=request.email,
        password=request.password,
    )
    
    response.set_cookie(
        key="access_token",
        value=tokens["access_token"],
        httponly=True,
        secure=settings.auth_cookie_secure,
        samesite=settings.auth_cookie_samesite,
        path="/",
        max_age=settings.access_token_ttl_minutes * 60,
    )
    
    response.set_cookie(
        key="refresh_token",
        value=tokens["refresh_token"],
        httponly=True,
        secure=settings.auth_cookie_secure,
        samesite=settings.auth_cookie_samesite,
        path="/",
        max_age=settings.refresh_token_ttl_days * 24 * 60 * 60,
    )

    return TokenResponse(access_token=tokens["access_token"], token_type="bearer")

@router.post("/refresh", response_model=TokenResponse)
def refresh(request: Request, response: Response, session: DatabaseSession):
    auth_service = create_auth_service(session=session)
    refresh_token_str = request.cookies.get("refresh_token")
    if not refresh_token_str:
        return Response(status_code=status.HTTP_401_UNAUTHORIZED)
        
    tokens = auth_service.refresh(refresh_token_str=refresh_token_str)
    
    response.set_cookie(
        key="access_token",
        value=tokens["access_token"],
        httponly=True,
        secure=settings.auth_cookie_secure,
        samesite=settings.auth_cookie_samesite,
        path="/",
        max_age=settings.access_token_ttl_minutes * 60,
    )
    
    response.set_cookie(
        key="refresh_token",
        value=tokens["refresh_token"],
        httponly=True,
        secure=settings.auth_cookie_secure,
        samesite=settings.auth_cookie_samesite,
        path="/",
        max_age=settings.refresh_token_ttl_days * 24 * 60 * 60,
    )

    return TokenResponse(access_token=tokens["access_token"], token_type="bearer")

@router.post("/logout")
def logout(request: Request, response: Response, session: DatabaseSession):
    auth_service = create_auth_service(session=session)
    refresh_token_str = request.cookies.get("refresh_token")
    if refresh_token_str:
        auth_service.logout(refresh_token_str=refresh_token_str)
        
    response.delete_cookie(key="access_token", path="/")
    response.delete_cookie(key="refresh_token", path="/")
    return {"message": "Logged out successfully"}

@router.get("/me", response_model=UserResponse)
def get_me(current_user: CurrentUser):
    return UserResponse.model_validate(current_user)
