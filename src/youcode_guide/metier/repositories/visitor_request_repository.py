from collections.abc import Callable
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from youcode_guide.database.sqlite.schema.consent_grant_table import ConsentGrantTable
from youcode_guide.database.sqlite.schema.visitor_request_table import VisitorRequestTable


class VisitorRequestRepository:
    def __init__(
        self,
        session_factory: Callable[
            [],
            Session,
        ],
    ) -> None:
        self.session_factory = session_factory

    def create_with_consent(
        self,
        visitor_request: VisitorRequestTable,
        consent_id: str,
        used_at: datetime,
    ) -> VisitorRequestTable:
        with self.session_factory() as session:
            consent = session.get(
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

            session.add(visitor_request)

            # La demande et le consentement sont
            # modifiés dans la même transaction.
            session.commit()
            session.refresh(visitor_request)

            return visitor_request

    def find_active_waitlist(
        self,
        email: str,
    ) -> VisitorRequestTable | None:
        active_statuses = [
            "pending",
            "in_progress",
        ]

        with self.session_factory() as session:
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

            return session.scalar(statement)

    def find_by_reference(
        self,
        reference: str,
    ) -> VisitorRequestTable | None:
        with self.session_factory() as session:
            statement = select(
                VisitorRequestTable
            ).where(
                VisitorRequestTable.reference
                == reference
            )

            return session.scalar(statement)

    def list_all(
        self,
    ) -> list[VisitorRequestTable]:
        with self.session_factory() as session:
            statement = (
                select(VisitorRequestTable)
                .order_by(
                    VisitorRequestTable
                    .created_at
                    .desc()
                )
            )

            return list(
                session.scalars(
                    statement
                ).all()
            )