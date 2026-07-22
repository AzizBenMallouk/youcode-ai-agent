"""Tests LOT 2 — Endpoints Newsletter."""

import pytest
from uuid import uuid4
from datetime import datetime, timezone, timedelta

from youcode_ai.domain.enums.common import Language
from youcode_ai.domain.enums.newsletter import (
    NewsletterTopic,
    SubscriptionStatus,
)
from youcode_ai.domain.enums.campaign import CampaignStatus
from youcode_ai.infrastructure.database.tables.newsletter_subscription import (
    NewsletterSubscriptionTable,
)
from youcode_ai.infrastructure.database.tables.newsletter_preference import (
    NewsletterPreferenceTable,
)
from youcode_ai.infrastructure.database.tables.newsletter_campaign import (
    NewsletterCampaignTable,
)
from youcode_ai.infrastructure.database.tables.email_delivery import (
    EmailDeliveryTable,
)
from youcode_ai.infrastructure.database.tables.consent import (
    ConsentGrantTable,
)
from youcode_ai.application.services.newsletter import NewsletterService
from youcode_ai.application.services.email import EmailService
from youcode_ai.infrastructure.email.console_provider import ConsoleEmailGateway


class TestNewsletterCampaignRepository:
    def test_create_campaign(self, db_session):
        campaign = NewsletterCampaignTable(
            reference="CAMPAIGN-123",
            title="Test Campaign",
            subject="Hello World",
            target_topics='["bootcamps"]',
            target_campuses='["Youssoufia"]',
            status=CampaignStatus.DRAFT,
        )
        db_session.add(campaign)
        db_session.commit()

        assert campaign.id is not None
        assert campaign.reference == "CAMPAIGN-123"

class TestNewsletterService:
    def test_create_campaign(self, db_session):
        service = NewsletterService(
            session=db_session,
        )
        
        campaign = service.create_campaign({
            "title": "Summer Bootcamps",
            "subject": "Learn to code this summer!",
            "template_name": "newsletter_content",
            "content": "<p>Join us!</p>",
            "target_topics": ["bootcamps"],
            "target_campuses": ["Youssoufia"],
            "target_languages": ["fr"],
        })
        
        assert campaign.id is not None
        assert campaign.reference is not None
        assert campaign.status == CampaignStatus.DRAFT
        
    def test_send_campaign(self, db_session):
        service = NewsletterService(
            session=db_session,
        )
        
        consent1 = ConsentGrantTable(
            id=str(uuid4()),
            reference="CONS-123",
            session_id="session1",
            purpose="newsletter",
            subject_hash="hash1",
            token_hash="token1",
            consent_version="1.0",
            created_at=datetime.now(timezone.utc),
            expires_at=datetime.now(timezone.utc) + timedelta(days=1),
        )
        consent2 = ConsentGrantTable(
            id=str(uuid4()),
            reference="CONS-124",
            session_id="session2",
            purpose="newsletter",
            subject_hash="hash2",
            token_hash="token2",
            consent_version="1.0",
            created_at=datetime.now(timezone.utc),
            expires_at=datetime.now(timezone.utc) + timedelta(days=1),
        )
        db_session.add_all([consent1, consent2])
        db_session.commit()
        
        # Create subscription 1 (matches)
        sub1 = NewsletterSubscriptionTable(
            email="user1@example.com",
            language=Language.FR,
            status=SubscriptionStatus.ACTIVE,
            campus="Youssoufia",
            consent_id=consent1.id
        )
        sub1.preferences.append(NewsletterPreferenceTable(topic=NewsletterTopic.BOOTCAMPS))
        
        # Create subscription 2 (doesn't match campus)
        sub2 = NewsletterSubscriptionTable(
            email="user2@example.com",
            language=Language.FR,
            status=SubscriptionStatus.ACTIVE,
            campus="Safi",
            consent_id=consent2.id
        )
        sub2.preferences.append(NewsletterPreferenceTable(topic=NewsletterTopic.BOOTCAMPS))
        
        db_session.add_all([sub1, sub2])
        db_session.commit()
        
        campaign = service.create_campaign({
            "title": "Summer Bootcamps Youssoufia",
            "subject": "Learn to code!",
            "template_name": "newsletter_content",
            "content": "<p>Join us!</p>",
            "target_topics": [NewsletterTopic.BOOTCAMPS.value],
            "target_campuses": ["Youssoufia"],
            "target_languages": [Language.FR.value],
        })
        
        result = service.send_campaign(campaign.id)
        
        assert result["queued_count"] == 1
        
        db_session.refresh(campaign)
        assert campaign.status == CampaignStatus.SENDING
        assert campaign.total_recipients == 1
        
        # Check outbox
        deliveries = db_session.query(EmailDeliveryTable).all()
        assert len(deliveries) == 1
        assert deliveries[0].recipient_email == "user1@example.com"
