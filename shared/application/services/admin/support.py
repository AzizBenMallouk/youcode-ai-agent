from datetime import (
    datetime,
    timezone,
)

from sqlalchemy.orm import Session
from shared.infrastructure.database.repositories.visitor_request import (
    VisitorRequestRepository,
)
from shared.infrastructure.database.tables import (
    VisitorRequestTable,
)


class SupportRequestNotFoundError(LookupError):
    pass


class InvalidSupportTransitionError(ValueError):
    pass


class SupportAdminService:
    def __init__(
        self,
        *,
        session: Session,
    ) -> None:
        self.repository = VisitorRequestRepository(session=session)

    def list_requests(
        self,
        *,
        page: int,
        page_size: int,
        request_type: str | None = None,
        status: str | None = None,
        campus: str | None = None,
    ) -> tuple[
        list[VisitorRequestTable],
        int,
    ]:
        return self.repository.list_filtered(
            page=page,
            page_size=page_size,
            request_type=request_type,
            status=status,
            campus=campus,
        )

    def get_request(
        self,
        *,
        reference: str,
    ) -> VisitorRequestTable:
        request = self.repository.find_by_reference(reference)

        if request is None:
            raise SupportRequestNotFoundError("Support request not found.")

        return request

    def approve(
        self,
        *,
        reference: str,
        note: str | None = None,
    ) -> VisitorRequestTable:
        """
        Approuve une proposition de report.

        L'envoi d'e-mail sera traité séparément
        dans la prochaine étape du projet.
        """

        request = self.get_request(reference=reference)

        if request.request_type != "test_reschedule":
            raise InvalidSupportTransitionError(
                "Only test rescheduling requests can use this approval workflow."
            )

        if request.status != "pending_approval":
            raise InvalidSupportTransitionError(
                "Only a pending approval request can be approved."
            )

        if not request.external_session_id or not request.proposed_test_date:
            raise InvalidSupportTransitionError(
                "The request has no valid proposed session."
            )

        now = datetime.now(timezone.utc)

        request.status = "approved"
        request.review_note = note
        request.reviewed_at = now
        request.updated_at = now

        return self.repository.save(request)

    def reject(
        self,
        *,
        reference: str,
        reason: str,
    ) -> VisitorRequestTable:
        request = self.get_request(reference=reference)

        terminal_statuses = {
            "approved",
            "rejected",
            "completed",
            "cancelled",
        }

        if request.status in terminal_statuses:
            raise InvalidSupportTransitionError(
                "A completed request cannot be rejected."
            )

        now = datetime.now(timezone.utc)

        request.status = "rejected"
        request.review_note = reason
        request.reviewed_at = now
        request.updated_at = now

        return self.repository.save(request)
