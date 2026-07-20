import secrets
from datetime import datetime, timezone
from uuid import uuid4

from youcode_guide.metier.enums.consent_purpose import (
    ConsentPurpose,
)
from youcode_guide.metier.services.consent_service import (
    ConsentService,
    create_consent_service,
)
from youcode_guide.database.sqlite.connection import (
    create_database_session,
)
from youcode_guide.database.sqlite.schema.visitor_request_table import (
    VisitorRequestTable,
)
from youcode_guide.metier.enums.registration_state import (
    RegistrationState,
)
from youcode_guide.metier.services.registration_service import (
    RegistrationService,
    create_registration_service,
)
from youcode_guide.metier.enums.request_status import RequestStatus
from youcode_guide.metier.enums.request_type import RequestType
from youcode_guide.metier.models.test_reschedule_request import TestRescheduleRequest
from youcode_guide.metier.models.waitlist_request import WaitlistRequest
from youcode_guide.metier.models.visitor_request_result import VisitorRequestResult
from youcode_guide.metier.models.access_support_request import AccessSupportRequest

from youcode_guide.metier.repositories.visitor_request_repository import (
    VisitorRequestRepository,
)


class VisitorRequestService:
    def __init__(
        self,
        repository: VisitorRequestRepository,
        consent_service: ConsentService,
        registration_service: (
            RegistrationService
        ),
    ) -> None:
        self.repository = repository

        self.consent_service = (
            consent_service
        )

        self.registration_service = (
            registration_service
        )

    def create_waitlist(
        self,
        request: WaitlistRequest,
    ) -> VisitorRequestResult:
        registration = (
            self.registration_service
            .get_current_status()
        )

        if (
            registration.status
            == RegistrationState.OPEN
        ):
            raise ValueError(
                "Registrations are open. "
                "Use the official registration URL."
            )

        if (
            registration.status
            == RegistrationState.UNKNOWN
        ):
            raise ValueError(
                "Registration status is unknown. "
                "The waitlist cannot be created."
            )

        normalized_email = self._normalize_email(
            str(request.email)
        )

        existing_request = (
            self.repository
            .find_active_waitlist(
                normalized_email
            )
        )

        if existing_request is not None:
            return VisitorRequestResult(
                reference=(
                    existing_request.reference
                ),
                request_type=(
                    RequestType.WAITLIST
                ),
                status=RequestStatus(
                    existing_request.status
                ),
                created_at=(
                    existing_request.created_at
                ),
                message=(
                    "Une demande active existe "
                    "déjà pour cet email."
                ),
            )

        verified_consent = (
            self.consent_service.verify(
                token=request.consent_token,
                session_id=request.session_id,
                purpose=(
                    ConsentPurpose
                    .WAITLIST_NOTIFICATION
                ),
                email=normalized_email,
            )
        )

        row = self._create_request(
            request_type=RequestType.WAITLIST,
            email=normalized_email,
            language=request.language.value,
            consent_id=(
                verified_consent.consent_id
            ),
            campus=request.campus,
        )

        return self._build_result(row)

    def create_access_support(
        self,
        request: AccessSupportRequest,
    ) -> VisitorRequestResult:
        normalized_email = self._normalize_email(
            str(request.email)
        )

        verified_consent = (
            self.consent_service.verify(
                token=request.consent_token,
                session_id=request.session_id,
                purpose=(
                    ConsentPurpose
                    .ACCESS_SUPPORT
                ),
                email=normalized_email,
            )
        )

        row = self._create_request(
            request_type=(
                RequestType.ACCESS_PROBLEM
            ),
            email=normalized_email,
            language=request.language.value,
            consent_id=(
                verified_consent.consent_id
            ),
            platform=request.platform,
            description=request.description,
        )

        return self._build_result(row)

    def create_test_reschedule(
        self,
        request: TestRescheduleRequest,
    ) -> VisitorRequestResult:
        normalized_email = self._normalize_email(
            str(request.email)
        )

        verified_consent = (
            self.consent_service.verify(
                token=request.consent_token,
                session_id=request.session_id,
                purpose=(
                    ConsentPurpose
                    .TEST_RESCHEDULE
                ),
                email=normalized_email,
            )
        )

        row = self._create_request(
            request_type=(
                RequestType.TEST_RESCHEDULE
            ),
            email=normalized_email,
            language=request.language.value,
            consent_id=(
                verified_consent.consent_id
            ),
            description=request.description,
            scheduled_test_date=(
                request.scheduled_test_date
            ),
            requested_test_date=(
                request.requested_test_date
            ),
        )

        return self._build_result(row)

    def _create_request(
        self,
        request_type: RequestType,
        email: str,
        language: str,
        consent_id: str,
        campus: str | None = None,
        platform: str | None = None,
        description: str | None = None,
        scheduled_test_date=None,
        requested_test_date=None,
    ) -> VisitorRequestTable:
        now = datetime.now(timezone.utc)

        reference = (
            f"YC-{self._reference_prefix(request_type)}-"
            f"{secrets.token_hex(4).upper()}"
        )

        row = VisitorRequestTable(
            id=str(uuid4()),
            reference=reference,
            request_type=request_type.value,
            status=RequestStatus.PENDING.value,
            email=email,
            language=language,
            campus=campus,
            platform=platform,
            description=description,
            scheduled_test_date=(
                scheduled_test_date
            ),
            requested_test_date=(
                requested_test_date
            ),
            consent_id=consent_id,
            created_at=now,
            updated_at=now,
        )

        return (
            self.repository
            .create_with_consent(
                visitor_request=row,
                consent_id=consent_id,
                used_at=now,
            )
        )

    def _build_result(
        self,
        row: VisitorRequestTable,
    ) -> VisitorRequestResult:
        request_type = RequestType(
            row.request_type
        )

        messages = {
            RequestType.WAITLIST: (
                "Votre demande de notification "
                "a été enregistrée."
            ),
            RequestType.ACCESS_PROBLEM: (
                "Votre problème d'accès a été "
                "transmis pour traitement."
            ),
            RequestType.TEST_RESCHEDULE: (
                "Votre demande de report a été "
                "enregistrée. Elle doit être "
                "examinée par un responsable."
            ),
        }

        return VisitorRequestResult(
            reference=row.reference,
            request_type=request_type,
            status=RequestStatus(row.status),
            created_at=row.created_at,
            message=messages[request_type],
        )

    def _normalize_email(
        self,
        email: str,
    ) -> str:
        return email.strip().lower()

    def _reference_prefix(
        self,
        request_type: RequestType,
    ) -> str:
        prefixes = {
            RequestType.WAITLIST: "WAIT",
            RequestType.ACCESS_PROBLEM: "ACCESS",
            RequestType.TEST_RESCHEDULE: "TEST",
        }

        return prefixes[request_type]


def create_visitor_request_service(
) -> VisitorRequestService:
    repository = VisitorRequestRepository(
        session_factory=(
            create_database_session
        )
    )

    return VisitorRequestService(
        repository=repository,
        consent_service=(
            create_consent_service()
        ),
        registration_service=(
            create_registration_service()
        ),
    )