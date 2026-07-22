"""Tests LOT 1 — Système d'e-mails."""

import json
import logging
from unittest.mock import MagicMock, patch

import pytest

from youcode_ai.application.ports.email_gateway import (
    EmailDeliveryResult,
    EmailMessage,
)
from youcode_ai.application.services.email import (
    EmailService,
)
from youcode_ai.domain.enums import (
    EmailDeliveryStatus,
    EmailType,
)
from youcode_ai.infrastructure.database.repositories.email_delivery import (
    EmailDeliveryRepository,
)
from youcode_ai.infrastructure.database.tables.email_delivery import (
    EmailDeliveryTable,
)
from youcode_ai.infrastructure.email.console_provider import (
    ConsoleEmailGateway,
)
from youcode_ai.infrastructure.email.templates import (
    EmailTemplateRenderer,
)


class TestEmailOutboxCreation:
    """Test de création d'entrées outbox."""

    def test_queue_email_creates_delivery(
        self, db_session
    ):
        gateway = ConsoleEmailGateway()
        service = EmailService(
            session=db_session,
            gateway=gateway,
        )

        delivery = service.queue_email(
            recipient="test@example.com",
            email_type=(
                EmailType.SUBSCRIPTION_CONFIRMATION
            ),
            template_name=(
                "newsletter_confirmation"
            ),
            payload={
                "topics": "Bootcamps, Events",
                "unsubscribe_url": (
                    "https://example.com/unsub"
                ),
            },
        )

        assert delivery.id is not None
        assert (
            delivery.recipient_email
            == "test@example.com"
        )
        assert delivery.status == (
            EmailDeliveryStatus.PENDING
        )
        assert delivery.attempts == 0
        assert delivery.template_name == (
            "newsletter_confirmation"
        )
        assert delivery.payload_json is not None

    def test_queue_email_normalizes_recipient(
        self, db_session
    ):
        gateway = ConsoleEmailGateway()
        service = EmailService(
            session=db_session,
            gateway=gateway,
        )

        delivery = service.queue_email(
            recipient="  Test@Example.COM  ",
            email_type=(
                EmailType.SUPPORT_ACKNOWLEDGEMENT
            ),
            template_name=(
                "support_acknowledgement"
            ),
            payload={"reference": "VR-123"},
        )

        assert (
            delivery.recipient_email
            == "test@example.com"
        )


class TestConsoleProvider:
    """Test du provider de développement."""

    def test_console_provider_succeeds(self):
        provider = ConsoleEmailGateway()

        result = provider.send(
            EmailMessage(
                recipient="user@test.com",
                subject="Test",
                body_html="<p>Hello</p>",
                body_text="Hello",
            )
        )

        assert result.success is True
        assert (
            result.provider_message_id
            is not None
        )
        assert (
            result.provider_message_id.startswith(
                "console-"
            )
        )

    def test_console_provider_logs(
        self, caplog
    ):
        provider = ConsoleEmailGateway()

        with caplog.at_level(
            logging.INFO
        ):
            provider.send(
                EmailMessage(
                    recipient=(
                        "user@test.com"
                    ),
                    subject="Test Subject",
                    body_html="<p>Hello</p>",
                )
            )

        assert "user@test.com" in caplog.text
        assert "Test Subject" in caplog.text


class TestSmtpProviderMock:
    """Test SMTP avec mock."""

    def test_smtp_success(self, db_session):
        mock_gateway = MagicMock()
        mock_gateway.send.return_value = (
            EmailDeliveryResult(
                success=True,
                provider_message_id=(
                    "smtp-12345"
                ),
            )
        )

        service = EmailService(
            session=db_session,
            gateway=mock_gateway,
        )

        delivery = service.queue_email(
            recipient="user@test.com",
            email_type=(
                EmailType.NEWSLETTER
            ),
            template_name=(
                "newsletter_content"
            ),
            payload={
                "subject": "News",
                "content": "Hello",
                "unsubscribe_url": (
                    "https://x.com/unsub"
                ),
            },
        )

        service.process_pending()

        db_session.refresh(delivery)
        assert delivery.status == (
            EmailDeliveryStatus.SENT
        )
        assert (
            delivery.provider_message_id
            == "smtp-12345"
        )
        assert delivery.sent_at is not None

    def test_smtp_failure_and_retry(
        self, db_session
    ):
        mock_gateway = MagicMock()
        mock_gateway.send.return_value = (
            EmailDeliveryResult(
                success=False,
                error_message=(
                    "Connection refused"
                ),
            )
        )

        service = EmailService(
            session=db_session,
            gateway=mock_gateway,
        )

        delivery = service.queue_email(
            recipient="user@test.com",
            email_type=(
                EmailType.NEWSLETTER
            ),
            template_name=(
                "newsletter_content"
            ),
            payload={
                "subject": "Test",
                "content": "Hello",
                "unsubscribe_url": "#",
            },
        )

        # Premier échec → reste PENDING
        # pour retry
        service.process_pending()
        db_session.refresh(delivery)
        assert delivery.attempts == 1
        assert delivery.status == (
            EmailDeliveryStatus.PENDING
        )
        assert (
            delivery.error_message
            == "Connection refused"
        )


class TestNoDuplicateSend:
    """Test empêchant un double envoi."""

    def test_already_sent_skipped(
        self, db_session
    ):
        mock_gateway = MagicMock()
        mock_gateway.send.return_value = (
            EmailDeliveryResult(
                success=True,
                provider_message_id="ok",
            )
        )

        service = EmailService(
            session=db_session,
            gateway=mock_gateway,
        )

        delivery = service.queue_email(
            recipient="user@test.com",
            email_type=(
                EmailType.NEWSLETTER
            ),
            template_name=(
                "newsletter_content"
            ),
            payload={
                "subject": "T",
                "content": "C",
                "unsubscribe_url": "#",
            },
        )

        # Envoi initial
        service.process_pending()
        db_session.refresh(delivery)
        assert delivery.status == (
            EmailDeliveryStatus.SENT
        )

        # Deuxième appel ne renvoie pas
        call_count_before = (
            mock_gateway.send.call_count
        )
        service.process_pending()
        assert (
            mock_gateway.send.call_count
            == call_count_before
        )


class TestEmailTemplates:
    """Test des templates e-mail."""

    def test_reschedule_template(self):
        renderer = EmailTemplateRenderer()

        subject, html, text = (
            renderer.render(
                "test_reschedule_confirmation",
                {
                    "reference": "VR-ABC123",
                    "campus": "Safi",
                    "new_date": "15/08/2026",
                    "new_time": "09:00",
                },
            )
        )

        assert "report" in subject.lower()
        assert "VR-ABC123" in html
        assert "Safi" in html
        assert "15/08/2026" in text

    def test_support_template(self):
        renderer = EmailTemplateRenderer()

        subject, html, text = (
            renderer.render(
                "support_acknowledgement",
                {
                    "reference": "VR-XYZ789",
                },
            )
        )

        assert "réception" in subject.lower()
        assert "VR-XYZ789" in html

    def test_newsletter_template(self):
        renderer = EmailTemplateRenderer()

        subject, html, text = (
            renderer.render(
                "newsletter_confirmation",
                {
                    "topics": (
                        "Bootcamps, Events"
                    ),
                    "unsubscribe_url": (
                        "https://y.com/unsub"
                    ),
                },
            )
        )

        assert "abonnement" in subject.lower()
        assert "Bootcamps" in html


class TestNoSecretsInLogs:
    """Vérification que les logs ne
    contiennent pas de contenu sensible."""

    def test_console_provider_no_body_in_logs(
        self, caplog
    ):
        provider = ConsoleEmailGateway()

        with caplog.at_level(
            logging.DEBUG
        ):
            provider.send(
                EmailMessage(
                    recipient=(
                        "user@test.com"
                    ),
                    subject="Test",
                    body_html=(
                        "<p>Secret data: "
                        "password123</p>"
                    ),
                    body_text=(
                        "Secret: password123"
                    ),
                )
            )

        assert (
            "password123" not in caplog.text
        )
        assert (
            "Secret data" not in caplog.text
        )


class TestEmailDeliveryRepository:
    """Tests du repository email."""

    def test_get_pending_returns_pending(
        self, db_session
    ):
        repo = EmailDeliveryRepository(
            session=db_session
        )

        delivery = EmailDeliveryTable(
            recipient_email="a@b.com",
            email_type=(
                EmailType.NEWSLETTER
            ),
            subject="Test",
            status=(
                EmailDeliveryStatus.PENDING
            ),
            attempts=0,
        )
        repo.add(delivery)

        pending = repo.get_pending(
            batch_size=10
        )
        assert len(pending) >= 1
        assert any(
            d.id == delivery.id
            for d in pending
        )

    def test_get_pending_excludes_sent(
        self, db_session
    ):
        repo = EmailDeliveryRepository(
            session=db_session
        )

        delivery = EmailDeliveryTable(
            recipient_email="sent@b.com",
            email_type=(
                EmailType.NEWSLETTER
            ),
            subject="Sent",
            status=(
                EmailDeliveryStatus.SENT
            ),
            attempts=1,
        )
        repo.add(delivery)

        pending = repo.get_pending(
            batch_size=10
        )
        assert all(
            d.id != delivery.id
            for d in pending
        )

    def test_mark_sending(self, db_session):
        repo = EmailDeliveryRepository(
            session=db_session
        )

        delivery = EmailDeliveryTable(
            recipient_email="c@d.com",
            email_type=(
                EmailType.NEWSLETTER
            ),
            subject="Test",
            status=(
                EmailDeliveryStatus.PENDING
            ),
            attempts=0,
        )
        repo.add(delivery)

        repo.mark_sending(delivery)
        assert delivery.status == (
            EmailDeliveryStatus.SENDING
        )
        assert delivery.attempts == 1
