from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from youcode_ai.api.dependencies.database import get_database_session
from youcode_ai.application.services.factories import create_newsletter_service
from youcode_ai.api.schemas.newsletter import (
    AdminSubscriptionResponse,
    SubscriptionListResponse,
    CampaignCreateRequest,
    CampaignResponse,
    CampaignListResponse,
    CampaignSendResponse,
    DeliveryListResponse,
)

router = APIRouter(prefix="/admin/newsletter", tags=["Admin Newsletter"])

@router.get("/subscriptions", response_model=SubscriptionListResponse)
def list_subscriptions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: str | None = None,
    campus: str | None = None,
    language: str | None = None,
    topic: str | None = None,
    session: Session = Depends(get_database_session),
):
    service = create_newsletter_service(session=session)
    items, total = service.list_subscriptions_filtered(
        page=page,
        page_size=page_size,
        status=status,
        campus=campus,
        language=language,
        topic=topic,
    )
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size
    }

@router.get("/subscriptions/{id}")
def get_subscription(
    id: str,
    session: Session = Depends(get_database_session),
):
    service = create_newsletter_service(session=session)
    sub = service.get_subscription_by_id(id)
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return sub

@router.patch("/subscriptions/{id}")
def update_subscription_admin(
    id: str,
    status: str | None = None,
    campus: str | None = None,
    language: str | None = None,
    session: Session = Depends(get_database_session),
):
    service = create_newsletter_service(session=session)
    try:
        sub = service.update_subscription_admin(
            id=id, status=status, campus=campus, language=language
        )
        return sub
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/campaigns", response_model=CampaignResponse)
def create_campaign(
    request: CampaignCreateRequest,
    session: Session = Depends(get_database_session),
):
    service = create_newsletter_service(session=session)
    campaign = service.create_campaign(request.model_dump())
    return campaign

@router.get("/campaigns", response_model=CampaignListResponse)
def list_campaigns(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: str | None = None,
    session: Session = Depends(get_database_session),
):
    service = create_newsletter_service(session=session)
    items, total = service.list_campaigns(page=page, page_size=page_size, status=status)
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size
    }

@router.get("/campaigns/{id}")
def get_campaign(
    id: str,
    session: Session = Depends(get_database_session),
):
    service = create_newsletter_service(session=session)
    campaign = service.get_campaign(id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign

@router.post("/campaigns/{id}/send", response_model=CampaignSendResponse)
def send_campaign(
    id: str,
    session: Session = Depends(get_database_session),
):
    service = create_newsletter_service(session=session)
    try:
        result = service.send_campaign(id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/deliveries", response_model=DeliveryListResponse)
def list_deliveries(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    session: Session = Depends(get_database_session),
):
    raise HTTPException(status_code=501, detail="Not implemented")
