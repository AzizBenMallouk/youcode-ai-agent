import hashlib
import hmac
import secrets
from datetime import (
    datetime,
    timedelta,
    timezone,
)
from uuid import uuid4

from youcode_guide.config import settings
from youcode_guide.metier.models.consent_grant_result import ConsentGrantResult
from youcode_guide.metier.enums.consent_purpose import ConsentPurpose
from youcode_guide.metier.models.create_consent_grant import CreateConsentGrant
from youcode_guide.metier.models.verified_consent import VerifiedConsent

from youcode_guide.metier.repositories.consent_repository import (
    ConsentRepository,
)
from youcode_guide.database.sqlite.connection import (
    create_database_session,
)
from youcode_guide.database.sqlite.schema.consent_grant_table import (
    ConsentGrantTable,
)


class ConsentService:
    def __init__(
        self,
        repository: ConsentRepository,
        secret_key: str,
        token_ttl_minutes: int,
        consent_version: str,
    ) -> None:
        self.repository = repository
        self.secret_key = secret_key
        self.token_ttl_minutes = (
            token_ttl_minutes
        )
        self.consent_version = consent_version

    def create_grant(
        self,
        request: CreateConsentGrant,
    ) -> ConsentGrantResult:
        if not request.accepted:
            raise ValueError(
                "Explicit consent is required."
            )

        now = datetime.now(timezone.utc)

        expires_at = now + timedelta(
            minutes=self.token_ttl_minutes
        )

        raw_token = secrets.token_urlsafe(32)

        consent_id = str(uuid4())

        reference = (
            f"YC-CONSENT-"
            f"{secrets.token_hex(4).upper()}"
        )

        consent = ConsentGrantTable(
            id=consent_id,
            reference=reference,
            token_hash=self._hash_token(
                raw_token
            ),
            session_id=request.session_id,
            purpose=request.purpose.value,
            subject_hash=self._hash_email(
                str(request.email)
            ),
            consent_version=(
                self.consent_version
            ),
            created_at=now,
            expires_at=expires_at,
            used_at=None,
            revoked_at=None,
        )

        self.repository.create(consent)

        return ConsentGrantResult(
            reference=reference,
            token=raw_token,
            purpose=request.purpose,
            expires_at=expires_at,
        )

    def verify(
        self,
        token: str,
        session_id: str,
        purpose: ConsentPurpose,
        email: str,
    ) -> VerifiedConsent:
        token_hash = self._hash_token(token)

        consent = (
            self.repository.find_by_token_hash(
                token_hash
            )
        )

        if consent is None:
            raise ValueError(
                "Invalid consent token."
            )

        if consent.session_id != session_id:
            raise ValueError(
                "The consent belongs to another "
                "session."
            )

        if consent.purpose != purpose.value:
            raise ValueError(
                "The consent does not match "
                "this purpose."
            )

        if not hmac.compare_digest(
            consent.subject_hash,
            self._hash_email(email),
        ):
            raise ValueError(
                "The consent does not match "
                "this email."
            )

        if consent.revoked_at is not None:
            raise ValueError(
                "The consent was revoked."
            )

        if consent.used_at is not None:
            raise ValueError(
                "The consent token was already used."
            )

        expires_at = self._ensure_timezone(
            consent.expires_at
        )

        if expires_at <= datetime.now(
            timezone.utc
        ):
            raise ValueError(
                "The consent token has expired."
            )

        return VerifiedConsent(
            consent_id=consent.id,
            reference=consent.reference,
            purpose=ConsentPurpose(
                consent.purpose
            ),
            expires_at=expires_at,
        )

    def mark_as_used(
        self,
        consent_id: str,
    ) -> None:
        self.repository.mark_as_used(
            consent_id=consent_id,
            used_at=datetime.now(
                timezone.utc
            ),
        )

    def _hash_token(
        self,
        token: str,
    ) -> str:
        return hashlib.sha256(
            token.encode("utf-8")
        ).hexdigest()

    def _hash_email(
        self,
        email: str,
    ) -> str:
        normalized_email = (
            email.strip().lower()
        )

        return hmac.new(
            self.secret_key.encode("utf-8"),
            normalized_email.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

    def _ensure_timezone(
        self,
        value: datetime,
    ) -> datetime:
        if value.tzinfo is None:
            return value.replace(
                tzinfo=timezone.utc
            )

        return value.astimezone(
            timezone.utc
        )


def create_consent_service(
) -> ConsentService:
    repository = ConsentRepository(
        session_factory=(
            create_database_session
        )
    )

    return ConsentService(
        repository=repository,
        secret_key=(
            settings.consent_secret_key
        ),
        token_ttl_minutes=(
            settings
            .consent_token_ttl_minutes
        ),
        consent_version=(
            settings.consent_version
        ),
    )