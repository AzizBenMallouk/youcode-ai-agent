from fastapi import APIRouter, Depends, Query
from youcode_ai.api.dependencies.database import DatabaseSession
from youcode_ai.api.dependencies.auth import require_roles
from youcode_ai.application.services.factories import create_admin_user_service
from youcode_ai.api.schemas.auth import CreateUserRequest, UpdateUserRequest, UserResponse, UserListResponse

router = APIRouter(
    prefix="/admin/users",
    tags=["Admin - Users"],
    dependencies=[Depends(require_roles("admin"))]
)

@router.post("", response_model=UserResponse)
def create_user(request: CreateUserRequest, session: DatabaseSession):
    service = create_admin_user_service(session=session)
    user = service.create_user(
        email=request.email,
        password=request.password,
        full_name=request.full_name,
        role=request.role,
    )
    return UserResponse.model_validate(user)

@router.get("", response_model=UserListResponse)
def list_users(
    session: DatabaseSession,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    role: str | None = None,
    is_active: bool | None = None,
):
    service = create_admin_user_service(session=session)
    users, total = service.list_users(page=page, page_size=page_size, role=role, is_active=is_active)
    
    return UserListResponse(
        items=[UserResponse.model_validate(u) for u in users],
        total=total,
        page=page,
        page_size=page_size,
    )

@router.patch("/{user_id}", response_model=UserResponse)
def update_user(user_id: str, request: UpdateUserRequest, session: DatabaseSession):
    service = create_admin_user_service(session=session)
    user = service.update_user(
        user_id=user_id,
        full_name=request.full_name,
        role=request.role,
        is_active=request.is_active,
    )
    return UserResponse.model_validate(user)
