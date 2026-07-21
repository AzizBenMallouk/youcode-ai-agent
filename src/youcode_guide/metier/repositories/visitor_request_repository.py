from collections.abc import Callable
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from youcode_guide.database.sqlite.schema.consent_grant_table import ConsentGrantTable
from youcode_guide.database.sqlite.schema.visitor_request_table import VisitorRequestTable


class VisitorRequestRepository:
    def __init__(
        self,
        session: Session,
    ) -> None:
        self.session = session

    def save(
        self,
        request: VisitorRequestTable,
    ) -> VisitorRequestTable:
        self.session.add(request)
        self.session.flush()
        self.session.refresh(request)

        return request

    def create_with_consent(
        self,
        visitor_request: VisitorRequestTable,
        consent_id: str,
        used_at: datetime,
    ) -> VisitorRequestTable:
        consent = self.session.get(
            ConsentGrantTable,
            consent_id,
        )

        if consent is None:
            raise ValueError(
                "Consent not found."
            )

        if consent.used_at is not None:
            raise ValueError(
                "Consent already used."
            )

        if consent.revoked_at is not None:
            raise ValueError(
                "Consent was revoked."
            )

        visitor_request.consent_id = (
            consent.id
        )

        consent.used_at = used_at

        self.session.add(visitor_request)

        # La demande et le consentement sont
        # modifiés dans la même transaction.
        self.session.commit()
        self.session.refresh(visitor_request)

        return visitor_request

    def find_active_waitlist(
        self,
        email: str,
    ) -> VisitorRequestTable | None:
        active_statuses = [
            "pending",
            "in_progress",
        ]

        statement = select(
            VisitorRequestTable
        ).where(
            VisitorRequestTable.email
            == email,
            VisitorRequestTable.request_type
            == "waitlist",
            VisitorRequestTable.status.in_(
                active_statuses
            ),
        )

        return self.session.scalar(statement)

    def find_by_reference(
        self,
        reference: str,
    ) -> VisitorRequestTable | None:
        statement = select(
            VisitorRequestTable
        ).where(
            VisitorRequestTable.reference
            == reference
        )

        return self.session.scalar(statement)


    def list_pending_rescheduling(
        self,
        *,
        limit: int = 100,
    ) -> list[VisitorRequestTable]:
        statement = (
            select(VisitorRequestTable)
            .where(
                VisitorRequestTable.request_type
                == "test_reschedule",
                VisitorRequestTable.status.in_(
                    [
                        "pending",
                        "processing",
                    ]
                ),
            )
            .order_by(
                VisitorRequestTable.created_at
            )
            .limit(limit)
        )

        return list(
            self.session.scalars(statement)
        )
        
    def update_status(
        self,
        request: VisitorRequestTable,
        status: str,
    ) -> VisitorRequestTable:
        request.status = status

        return self.save(request)

    def list_all(
        self,
    ) -> list[VisitorRequestTable]:
        statement = (
            select(VisitorRequestTable)
            .order_by(
                VisitorRequestTable
                .created_at
                .desc()
            )
        )

        return list(
            self.session.scalars(
                statement
            ).all()
        )