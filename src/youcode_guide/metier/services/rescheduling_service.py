from datetime import date, datetime, timezone
from sqlalchemy.orm import Session

from youcode_guide.database.sqlite.schema.visitor_request_table import (
    VisitorRequestTable,
)
from youcode_guide.metier.exceptions.rescheduling import (
    InvalidReschedulingRequest,
    ProposedSessionNotAvailable,
    ReschedulingAlreadyProcessed,
    ReschedulingRequestNotFound,
)
from youcode_guide.metier.models.rescheduling_context import (
    ReschedulingContext,
)
from youcode_guide.metier.models.test_session import (
    TestSession,
)
from youcode_guide.metier.repositories.visitor_request_repository import (
    VisitorRequestRepository,
)
from youcode_guide.metier.services.test_session_service import (
    create_test_session_service,
    TestSessionService
)


class ReschedulingService:
    def __init__(
        self,
        *,
        repository:
            VisitorRequestRepository,
        test_session_service:
            TestSessionService,
    ) -> None:
        self.repository = repository
        self.test_session_service = (
            test_session_service
        )

    def prepare_request(
        self,
        *,
        reference: str,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> ReschedulingContext:
        request = self._get_request(
            reference
        )

        self._validate_request(request)

        request.status = "processing"

        search_date = self._resolve_search_date(
            request=request,
            date_from=date_from,
        )

        sessions = (
            self.test_session_service
            .find_next_sessions(
                campus=request.campus,
                date_from=search_date,
                date_to=date_to,
            )
        )

        if not sessions:
            request.status = "pending_review"

            return ReschedulingContext(
                request_id=request.id,
                reference=request.reference,
                email=request.email,
                campus=request.campus,
                description=(
                    request.description
                ),
                scheduled_test_date=(
                    self._date_to_string(
                        request
                        .scheduled_test_date
                    )
                ),
                requested_test_date=(
                    self._date_to_string(
                        request
                        .requested_test_date
                    )
                ),
                available_sessions=[],
                requires_human=True,
                message=(
                    "No compatible test "
                    "session is available."
                ),
            )

        return ReschedulingContext(
            request_id=request.id,
            reference=request.reference,
            email=request.email,
            campus=request.campus,
            description=request.description,
            scheduled_test_date=(
                self._date_to_string(
                    request.scheduled_test_date
                )
            ),
            requested_test_date=(
                self._date_to_string(
                    request.requested_test_date
                )
            ),
            available_sessions=sessions,
        )

    def propose_session(
        self,
        *,
        reference: str,
        external_session_id: str,
        decision_reason: str,
    ) -> VisitorRequestTable:
        request = self._get_request(
            reference
        )

        self._validate_request(request)

        search_date = self._resolve_search_date(
            request=request,
            date_from=None,
        )

        sessions = (
            self.test_session_service
            .find_next_sessions(
                campus=request.campus,
                date_from=search_date,
                date_to=None,
            )
        )

        selected_session = next(
            (
                session
                for session in sessions
                if session.external_id
                == external_session_id
            ),
            None,
        )

        if selected_session is None:
            raise ProposedSessionNotAvailable(
                "The proposed session is no "
                "longer available."
            )

        request.external_session_id = (
            selected_session.external_id
        )

        request.proposed_test_date = (
            selected_session.scheduled_at
        )

        request.decision_reason = (
            decision_reason
        )

        request.status = "pending_approval"

        request.updated_at = datetime.now(
            timezone.utc
        )

        self.repository.save(request)

        return request

    def _get_request(
        self,
        reference: str,
    ) -> VisitorRequestTable:
        request = (
            self.repository.find_by_reference(
                reference
            )
        )

        if request is None:
            raise ReschedulingRequestNotFound(
                f"Request {reference} "
                "was not found."
            )

        return request

    @staticmethod
    def _validate_request(
        request: VisitorRequestTable,
    ) -> None:
        if (
            request.request_type
            != "test_reschedule"
        ):
            raise InvalidReschedulingRequest(
                "The request is not a "
                "rescheduling request."
            )

        if not request.campus:
            raise InvalidReschedulingRequest(
                "The campus is required."
            )

        if request.status in {
            "confirmed",
            "rejected",
            "cancelled",
        }:
            raise ReschedulingAlreadyProcessed(
                "The request is already closed."
            )

    @staticmethod
    def _resolve_search_date(
        *,
        request: VisitorRequestTable,
        date_from: date | None,
    ) -> date:
        today = date.today()

        candidates = [
            today,
        ]

        if date_from is not None:
            candidates.append(date_from)

        if (
            request.requested_test_date
            is not None
        ):
            candidates.append(
                request.requested_test_date
            )

        return max(candidates)

    @staticmethod
    def _date_to_string(
        value: date | None,
    ) -> str | None:
        if value is None:
            return None

        return value.isoformat()
    

def create_rescheduling_service(
    session: Session,
) -> ReschedulingService:
    repository = VisitorRequestRepository(
        session
    )

    return ReschedulingService(
        repository=repository,
        test_session_service=(
            create_test_session_service()
        ),
    )