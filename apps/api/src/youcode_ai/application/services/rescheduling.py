from datetime import (
    datetime,
    timezone,
)

from youcode_ai.application.schemas import (
    ReschedulingResult,
)
from youcode_ai.application.services.test_session import (
    TestSessionService,
)
from youcode_ai.domain.enums import (
    RequestStatus,
    RequestType,
)
from youcode_ai.domain.exceptions import (
    IncompleteRequestError,
    InvalidRequestStatusError,
    InvalidRequestTypeError,
    VisitorRequestNotFoundError,
)
from youcode_ai.infrastructure.database.repositories import (
    VisitorRequestRepository,
)


class ReschedulingService:
    def __init__(
        self,
        *,
        repository: (
            VisitorRequestRepository
        ),
        test_session_service: (
            TestSessionService
        ),
    ) -> None:
        self.repository = repository
        self.test_session_service = (
            test_session_service
        )

    def process(
        self,
        *,
        reference: str,
        session_id: str,
    ) -> ReschedulingResult:
        visitor_request = (
            self.repository
            .find_by_reference_for_session(
                reference=(
                    reference.strip().upper()
                ),
                session_id=session_id,
            )
        )

        if visitor_request is None:
            raise (
                VisitorRequestNotFoundError(
                    "Visitor request not found."
                )
            )

        if (
            visitor_request.request_type
            != RequestType.TEST_RESCHEDULE
        ):
            raise InvalidRequestTypeError(
                "The request is not a test "
                "rescheduling request."
            )

        if (
            visitor_request.status
            != RequestStatus.PENDING
        ):
            raise InvalidRequestStatusError(
                "Only pending requests can "
                "be processed."
            )

        if not visitor_request.campus:
            raise IncompleteRequestError(
                "The request has no campus."
            )

        if (
            visitor_request
            .scheduled_test_date
            is None
        ):
            raise IncompleteRequestError(
                "The current test date "
                "is missing."
            )

        if (
            visitor_request
            .requested_test_date
            is None
        ):
            raise IncompleteRequestError(
                "The requested test date "
                "is missing."
            )

        visitor_request.status = (
            RequestStatus.PROCESSING
        )

        self.repository.save(
            visitor_request
        )

        selected_session = (
            self.test_session_service
            .find_best_session(
                campus=(
                    visitor_request.campus
                ),
                requested_date=(
                    visitor_request
                    .requested_test_date
                ),
            )
        )

        # Nouvelle lecture de la session :
        # évite d'enregistrer une session qui
        # serait devenue fermée ou complète.
        validated_session = (
            self.test_session_service
            .validate_session(
                session_id=(
                    selected_session.id
                ),
                campus=(
                    visitor_request.campus
                ),
                requested_date=(
                    visitor_request
                    .requested_test_date
                ),
            )
        )

        decision_reason = (
            "Première session officielle "
            "disponible pour le campus de "
            f"{visitor_request.campus} à partir "
            "de la date souhaitée."
        )

        visitor_request.status = (
            RequestStatus.PENDING_APPROVAL
        )

        visitor_request.external_session_id = (
            validated_session.id
        )

        visitor_request.proposed_test_date = (
            validated_session.start_at
        )

        visitor_request.decision_reason = (
            decision_reason
        )

        visitor_request.processed_at = (
            datetime.now(timezone.utc)
        )

        visitor_request = (
            self.repository.save(
                visitor_request
            )
        )

        return ReschedulingResult(
            reference=(
                visitor_request.reference
            ),
            status=visitor_request.status,
            external_session_id=(
                visitor_request
                .external_session_id
            ),
            proposed_test_date=(
                visitor_request
                .proposed_test_date
            ),
            decision_reason=(
                visitor_request
                .decision_reason
            ),
            requires_human=True,
        )