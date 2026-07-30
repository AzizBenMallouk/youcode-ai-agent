import hashlib
import hmac
import json
import secrets
from dataclasses import dataclass
from datetime import (
    datetime,
    timedelta,
    timezone,
)
from uuid import uuid4

from sqlalchemy.orm import Session
from shared.core.config import settings
from shared.infrastructure.database.repositories.newsletter import (
    NewsletterRepository,
)

from shared.infrastructure.database.tables import (
    ConsentGrantTable,
    NewsletterSubscriptionTable,
)


@dataclass(frozen=True)
class NewsletterOperationResult:
    status: str
    reference: str | None


class NewsletterService:
    def __init__(
        self,
        *,
        session: Session,
    ) -> None:
        self.session = session

        self.repository = NewsletterRepository(session=session)

    def subscribe(
        self,
        *,
        session_id: str,
        email: str,
        language: str,
        topics: list[str],
        consent_confirmed: bool,
        phone_number: str | None = None,
        full_name: str | None = None,
        cin: str | None = None,
        campus: str | None = None,
    ) -> NewsletterOperationResult:
        """
        Crée ou réactive une inscription.

        Le consentement et l'inscription sont
        enregistrés dans la même transaction.
        """

        if not consent_confirmed:
            raise ValueError("Explicit newsletter consent is required.")

        if not topics:
            raise ValueError("At least one newsletter topic is required.")

        now = datetime.now(timezone.utc)

        normalized_email = email.strip().lower()

        consent = self._create_consent(
            session_id=session_id,
            email=normalized_email,
            now=now,
        )

        subscription = self.repository.find_by_email(normalized_email)

        if subscription is None:
            subscription = NewsletterSubscriptionTable(
                id=str(uuid4()),
                reference=(self._create_reference()),
                email=normalized_email,
                phone_number=phone_number,
                full_name=full_name,
                cin=cin,
                language=language,
                campus=campus,
                status="active",
                consent_id=consent.id,
                subscribed_at=now,
                unsubscribed_at=None,
                created_at=now,
                updated_at=now,
            )

            self.repository.add(subscription)

        else:
            self.repository.activate(
                subscription,
                language=language,
                consent_id=consent.id,
            )
            if campus is not None:
                subscription.campus = campus
            if phone_number is not None:
                subscription.phone_number = phone_number
            if full_name is not None:
                subscription.full_name = full_name
            if cin is not None:
                subscription.cin = cin

        self.repository.replace_preferences(
            subscription_id=subscription.id,
            topics=topics,
        )

        # Le consentement vient d'être utilisé
        # par cette inscription.
        consent.used_at = now

        self.session.flush()

        return NewsletterOperationResult(
            status="subscribed",
            reference=subscription.reference,
        )

    def unsubscribe(
        self,
        *,
        email: str,
    ) -> NewsletterOperationResult:
        """
        Désactive une inscription.

        La réponse reste volontairement neutre
        lorsque l'e-mail n'existe pas, afin de ne
        pas révéler les abonnements enregistrés.
        """

        normalized_email = email.strip().lower()

        subscription = self.repository.find_by_email(normalized_email)

        if subscription is None:
            return NewsletterOperationResult(
                status="unsubscribed",
                reference=None,
            )

        self.repository.deactivate(subscription)

        self.session.flush()

        return NewsletterOperationResult(
            status="unsubscribed",
            reference=subscription.reference,
        )

    def _create_consent(
        self,
        *,
        session_id: str,
        email: str,
        now: datetime,
    ) -> ConsentGrantTable:
        raw_token = secrets.token_urlsafe(32)

        token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()

        subject_hash = hmac.new(
            settings.consent_secret_key.encode("utf-8"),
            email.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

        identifier = uuid4().hex.upper()

        consent = ConsentGrantTable(
            id=str(uuid4()),
            reference=(f"CONS-NL-{identifier[:12]}"),
            token_hash=token_hash,
            session_id=session_id,
            purpose="newsletter",
            subject_hash=subject_hash,
            consent_version=(settings.consent_version),
            created_at=now,
            expires_at=(now + timedelta(minutes=settings.consent_token_ttl_minutes)),
            used_at=None,
            revoked_at=None,
        )

        self.session.add(consent)
        self.session.flush()

        return consent

    @staticmethod
    def _create_reference() -> str:
        identifier = uuid4().hex.upper()

        return f"NL-{identifier[:12]}"

    def list_subscriptions_filtered(
        self,
        *,
        page: int,
        page_size: int,
        status: str | None = None,
        campus: str | None = None,
        language: str | None = None,
        topic: str | None = None,
    ) -> tuple[list[NewsletterSubscriptionTable], int]:
        return self.repository.list_filtered(
            page=page,
            page_size=page_size,
            status=status,
            campus=campus,
            language=language,
            topic=topic,
        )

    def get_subscription_by_id(self, id: str) -> NewsletterSubscriptionTable | None:
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload

        statement = (
            select(NewsletterSubscriptionTable)
            .options(selectinload(NewsletterSubscriptionTable.preferences))
            .where(NewsletterSubscriptionTable.id == id)
        )
        return self.session.scalar(statement)

    def update_subscription_admin(
        self,
        *,
        id: str,
        status: str | None = None,
        campus: str | None = None,
        language: str | None = None,
    ) -> NewsletterSubscriptionTable:
        sub = self.get_subscription_by_id(id)
        if not sub:
            raise ValueError("Subscription not found")
        if status is not None:
            sub.status = status
        if campus is not None:
            sub.campus = campus
        if language is not None:
            sub.language = language
        self.session.flush()
        return sub


