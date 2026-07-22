import hashlib
import hmac
import secrets

from datetime import (
    datetime,
    timedelta,
    timezone,
)
from uuid import uuid4

from youcode_ai.application.schemas import (
    ConsentGrantResult,
)
from youcode_ai.core.config import settings
from youcode_ai.domain.enums import (
    ConsentPurpose,
)
from youcode_ai.domain.exceptions import (
    ConsentAlreadyRevokedError,
    ConsentNotFoundError,
)
from youcode_ai.infrastructure.database.repositories import (
    ConsentRepository,
)
from youcode_ai.infrastructure.database.tables import (
    ConsentGrantTable,
)


class ConsentService:
    def __init__(
        self,
        *,
        repository: ConsentRepository,
    ) -> None:
        self.repository = repository

    def create_grant(
        self,
        *,
        session_id: str,
        purpose: ConsentPurpose,
        subject: str,
    ) -> ConsentGrantResult:
        """
        Cette méthode doit uniquement être
        appelée après un consentement explicite.
        """

        normalized_subject = (
            self._normalize_subject(
                subject
            )
        )

        now = datetime.now(
            timezone.utc
        )

        raw_token = secrets.token_urlsafe(
            32
        )

        consent = ConsentGrantTable(
            reference=(
                self._generate_reference()
            ),
            session_id=session_id,
            purpose=purpose,
            subject_hash=(
                self._hash_subject(
                    normalized_subject
                )
            ),
            token_hash=(
                self._hash_token(
                    raw_token
                )
            ),
            consent_version=(
                settings.consent_version
            ),
            created_at=now,
            expires_at=(
                now
                + timedelta(
                    minutes=(
                        settings
                        .consent_token_ttl_minutes
                    )
                )
            ),
            # Le consentement vient d'être
            # explicitement confirmé.
            used_at=now,
            revoked_at=None,
        )

        consent = self.repository.add(
            consent
        )

        return ConsentGrantResult(
            id=consent.id,
            reference=consent.reference,
            purpose=consent.purpose,
            created_at=consent.created_at,
            used_at=consent.used_at,
        )

    def revoke(
        self,
        *,
        consent_id: str,
    ) -> None:
        consent = (
            self.repository.get_by_id(
                consent_id
            )
        )

        if consent is None:
            raise ConsentNotFoundError(
                "Consent not found."
            )

        if consent.revoked_at is not None:
            raise ConsentAlreadyRevokedError(
                "Consent is already revoked."
            )

        consent.revoked_at = datetime.now(
            timezone.utc
        )

        self.repository.save(
            consent
        )

    @staticmethod
    def _normalize_subject(
        subject: str,
    ) -> str:
        normalized = (
            subject.strip().lower()
        )

        if not normalized:
            raise ValueError(
                "Consent subject cannot "
                "be empty."
            )

        return normalized

    @staticmethod
    def _generate_reference() -> str:
        identifier = (
            uuid4().hex[:12].upper()
        )

        return f"CONS-{identifier}"

    @staticmethod
    def _hash_token(
        raw_token: str,
    ) -> str:
        return hashlib.sha256(
            raw_token.encode("utf-8")
        ).hexdigest()

    @staticmethod
    def _hash_subject(
        subject: str,
    ) -> str:
        return hmac.new(
            settings.consent_secret_key.encode(
                "utf-8"
            ),
            subject.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()