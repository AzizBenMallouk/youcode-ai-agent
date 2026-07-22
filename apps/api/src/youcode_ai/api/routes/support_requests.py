from fastapi import (
    APIRouter,
    HTTPException,
    Query,
    status,
    Depends,
)

from youcode_ai.api.dependencies.database import (
    DatabaseSession,
)
from youcode_ai.api.schemas.support_request import (
    ApproveSupportRequest,
    RejectSupportRequest,
    SupportRequestActionResponse,
    SupportRequestListResponse,
    SupportRequestResponse,
)
from youcode_ai.application.services.admin.support import (
    InvalidSupportTransitionError,
    SupportAdminService,
    SupportRequestNotFoundError,
)


from youcode_ai.api.dependencies.auth import require_roles

router = APIRouter(
    prefix="/admin/support-requests",
    tags=["Admin - Support Requests"],
    dependencies=[Depends(require_roles("admin", "support"))],
)


@router.get(
    "",
    response_model=(
        SupportRequestListResponse
    ),
)
def list_support_requests(
    session: DatabaseSession,
    page: int = Query(
        default=1,
        ge=1,
    ),
    page_size: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    request_type: str | None = Query(
        default=None
    ),
    request_status: str | None = Query(
        default=None,
        alias="status",
    ),
    campus: str | None = Query(
        default=None
    ),
) -> SupportRequestListResponse:
    service = SupportAdminService(
        session=session
    )

    requests, total = (
        service.list_requests(
            page=page,
            page_size=page_size,
            request_type=request_type,
            status=request_status,
            campus=campus,
        )
    )

    return SupportRequestListResponse(
        items=[
            SupportRequestResponse
            .model_validate(item)
            for item in requests
        ],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/{reference}",
    response_model=SupportRequestResponse,
)
def get_support_request(
    reference: str,
    session: DatabaseSession,
) -> SupportRequestResponse:
    service = SupportAdminService(
        session=session
    )

    try:
        request = service.get_request(
            reference=reference
        )

        return (
            SupportRequestResponse
            .model_validate(request)
        )

    except SupportRequestNotFoundError as error:
        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail=str(error),
        ) from error


@router.post(
    "/{reference}/approve",
    response_model=(
        SupportRequestActionResponse
    ),
)
def approve_support_request(
    reference: str,
    payload: ApproveSupportRequest,
    session: DatabaseSession,
) -> SupportRequestActionResponse:
    service = SupportAdminService(
        session=session
    )

    try:
        request = service.approve(
            reference=reference,
            note=payload.note,
        )

        return (
            SupportRequestActionResponse(
                reference=request.reference,
                status="approved",
                message=(
                    "La demande a été "
                    "approuvée."
                ),
            )
        )

    except SupportRequestNotFoundError as error:
        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail=str(error),
        ) from error

    except InvalidSupportTransitionError as error:
        raise HTTPException(
            status_code=(
                status.HTTP_409_CONFLICT
            ),
            detail=str(error),
        ) from error


@router.post(
    "/{reference}/reject",
    response_model=(
        SupportRequestActionResponse
    ),
)
def reject_support_request(
    reference: str,
    payload: RejectSupportRequest,
    session: DatabaseSession,
) -> SupportRequestActionResponse:
    service = SupportAdminService(
        session=session
    )

    try:
        request = service.reject(
            reference=reference,
            reason=payload.reason,
        )

        return (
            SupportRequestActionResponse(
                reference=request.reference,
                status="rejected",
                message=(
                    "La demande a été refusée."
                ),
            )
        )

    except SupportRequestNotFoundError as error:
        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail=str(error),
        ) from error

    except InvalidSupportTransitionError as error:
        raise HTTPException(
            status_code=(
                status.HTTP_409_CONFLICT
            ),
            detail=str(error),
        ) from error