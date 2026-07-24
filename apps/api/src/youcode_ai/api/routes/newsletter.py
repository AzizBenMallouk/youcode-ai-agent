from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from youcode_ai.api.dependencies.database import get_database_session
from youcode_ai.api.schemas.newsletter import (
    CreateSubscriptionRequest,
    UnsubscribeRequest,
    UpdatePreferencesRequest,
)
from youcode_ai.application.services.factories import create_newsletter_service

router = APIRouter(prefix="/newsletter", tags=["Newsletter"])


@router.post("/subscriptions", status_code=201)
def create_subscription(
    request: CreateSubscriptionRequest,
    session: Session = Depends(get_database_session),
):
    if not request.consent:
        raise HTTPException(status_code=400, detail="Consent is required")

    service = create_newsletter_service(session=session)

    try:
        result = service.subscribe(
            session_id="web",
            email=request.email,
            language=request.language,
            campus=request.campus,
            topics=request.topics,
            consent_confirmed=request.consent,
        )
        return {"status": "success", "reference": result.reference}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/subscriptions/{reference}")
def get_subscription(
    reference: str,
    token: str = Query(...),
    session: Session = Depends(get_database_session),
):
    # Minimal implementation for now
    raise HTTPException(status_code=501, detail="Not implemented")


@router.patch("/subscriptions/{reference}")
def update_subscription(
    reference: str,
    request: UpdatePreferencesRequest,
    session: Session = Depends(get_database_session),
):
    raise HTTPException(status_code=501, detail="Not implemented")


@router.post("/unsubscribe")
def unsubscribe(
    request: UnsubscribeRequest,
    session: Session = Depends(get_database_session),
):
    # Minimal idempotent implementation
    raise HTTPException(status_code=501, detail="Not implemented")
