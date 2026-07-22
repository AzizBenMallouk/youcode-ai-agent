from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class CreateSubscriptionRequest(BaseModel):
    email: EmailStr
    language: str = "fr"
    campus: str | None = None
    topics: list[str] = Field(min_length=1)
    consent: bool


class SubscriptionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    reference: str
    email: str
    language: str
    campus: str | None
    topics: list[str]
    status: str
    created_at: datetime


class UpdatePreferencesRequest(BaseModel):
    language: str | None = None
    campus: str | None = None
    topics: list[str] | None = None


class UnsubscribeRequest(BaseModel):
    token: str


class AdminSubscriptionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    email: str
    language: str
    campus: str | None
    status: str
    consent_id: str
    created_at: datetime
    updated_at: datetime


class SubscriptionListResponse(BaseModel):
    items: list[AdminSubscriptionResponse]
    total: int
    page: int
    page_size: int


class CampaignCreateRequest(BaseModel):
    title: str
    subject: str
    template_name: str = "newsletter_content"
    content: str | None = None
    target_topics: list[str] | None = None
    target_campuses: list[str] | None = None
    target_languages: list[str] | None = None


class CampaignResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    reference: str
    title: str
    subject: str
    status: str
    total_recipients: int
    total_sent: int
    total_failed: int
    created_at: datetime


class CampaignListResponse(BaseModel):
    items: list[CampaignResponse]
    total: int
    page: int
    page_size: int


class CampaignSendResponse(BaseModel):
    campaign_reference: str
    queued_count: int
    message: str


class DeliveryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    recipient_email: str
    email_type: str
    subject: str
    status: str
    created_at: datetime
    sent_at: datetime | None


class DeliveryListResponse(BaseModel):
    items: list[DeliveryResponse]
    total: int
    page: int
    page_size: int
