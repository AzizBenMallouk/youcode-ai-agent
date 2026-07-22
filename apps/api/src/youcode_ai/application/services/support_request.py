from uuid import uuid4

from youcode_ai.application.schemas import (
    SupportRequestCreate,
    SupportRequestResult,
)
from youcode_ai.application.services.consent import (
    ConsentService,
)
from youcode_ai.domain.enums import (
    ConsentPurpose,
    RequestStatus,
)
from youcode_ai.domain.exceptions import (
    DuplicateActiveRequestError,
)
from youcode_ai.infrastructure.database.repositories import (
    VisitorRequestRepository,
)
from youcode_ai.infrastructure.database.tables import (
    VisitorRequestTable,
)


class SupportRequestService:
    def __init__(
        self,
        *,
        repository: (
            VisitorRequestRepository
        ),
        consent_service: ConsentService,
    ) -> None:
        self.repository = repository
        self.consent_service = (
            consent_service
        )

    def create_request(
        self,
        data: SupportRequestCreate,
    ) -> SupportRequestResult:
        email = str(data.email).lower()

        existing_request = (
            self.repository
            .find_active_by_email_and_type(
                email=email,
                request_type=(
                    data.request_type
                ),
            )
        )

        if existing_request is not None:
            raise DuplicateActiveRequestError(
                "An active request already "
                "exists for this email and type. "
                f"Reference: "
                f"{existing_request.reference}"
            )

        # Le Support Agent appelle cette méthode
        # uniquement après une réponse "oui".
        consent = (
            self.consent_service
            .create_grant(
                session_id=data.session_id,
                purpose=(
                    ConsentPurpose
                    .SUPPORT_REQUEST
                ),
                subject=email,
            )
        )

        visitor_request = (
            VisitorRequestTable(
                reference=(
                    self._generate_reference()
                ),
                request_type=(
                    data.request_type
                ),
                status=(
                    RequestStatus.PENDING
                ),
                email=email,
                language=data.language,
                campus=(
                    data.campus.strip()
                    if data.campus
                    else None
                ),
                description=(
                    data.description.strip()
                ),
                scheduled_test_date=(
                    data.scheduled_test_date
                ),
                requested_test_date=(
                    data.requested_test_date
                ),
                external_session_id=None,
                proposed_test_date=None,
                decision_reason=None,
                processed_at=None,
                consent_id=consent.id,
            )
        )

        visitor_request = (
            self.repository.add(
                visitor_request
            )
        )

        return SupportRequestResult(
            id=visitor_request.id,
            reference=(
                visitor_request.reference
            ),
            request_type=(
                visitor_request.request_type
            ),
            status=visitor_request.status,
            email=visitor_request.email,
            language=(
                visitor_request.language
            ),
            campus=visitor_request.campus,
            scheduled_test_date=(
                visitor_request
                .scheduled_test_date
            ),
            requested_test_date=(
                visitor_request
                .requested_test_date
            ),
            consent_reference=(
                consent.reference
            ),
            created_at=(
                visitor_request.created_at
            ),
        )

    @staticmethod
    def _generate_reference() -> str:
        identifier = (
            uuid4().hex[:12].upper()
        )

        return f"VR-{identifier}"