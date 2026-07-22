from sqlalchemy import select
from sqlalchemy.orm import Session

from youcode_ai.domain.enums import (
    RequestStatus,
    RequestType,
)
from youcode_ai.infrastructure.database.repositories.base import (
    BaseRepository,
)
from youcode_ai.infrastructure.database.tables import (
    VisitorRequestTable,
    ConsentGrantTable,
)

class VisitorRequestRepository(
    BaseRepository[VisitorRequestTable]
):
    def __init__(
        self,
        *,
        session: Session,
    ) -> None:
        super().__init__(
            session=session,
            model_type=VisitorRequestTable,
        )

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

        return self.session.scalar(
            statement
        )

    def list_by_status(
        self,
        *,
        status: RequestStatus,
        limit: int = 100,
        offset: int = 0,
    ) -> list[VisitorRequestTable]:
        statement = (
            select(VisitorRequestTable)
            .where(
                VisitorRequestTable.status
                == status
            )
            .order_by(
                VisitorRequestTable
                .created_at
                .desc()
            )
            .offset(offset)
            .limit(limit)
        )

        return list(
            self.session.scalars(
                statement
            ).all()
        )

    def list_by_type(
        self,
        *,
        request_type: RequestType,
        limit: int = 100,
        offset: int = 0,
    ) -> list[VisitorRequestTable]:
        statement = (
            select(VisitorRequestTable)
            .where(
                VisitorRequestTable
                .request_type
                == request_type
            )
            .order_by(
                VisitorRequestTable
                .created_at
                .desc()
            )
            .offset(offset)
            .limit(limit)
        )

        return list(
            self.session.scalars(
                statement
            ).all()
        )

    def list_pending_support_requests(
        self,
        *,
        limit: int = 100,
    ) -> list[VisitorRequestTable]:
        statement = (
            select(VisitorRequestTable)
            .where(
                VisitorRequestTable.status.in_(
                    [
                        RequestStatus.PENDING,
                        RequestStatus.PROCESSING,
                    ]
                )
            )
            .order_by(
                VisitorRequestTable
                .created_at
                .asc()
            )
            .limit(limit)
        )

        return list(
            self.session.scalars(
                statement
            ).all()
        )

    def find_active_by_email_and_type(
        self,
        *,
        email: str,
        request_type: RequestType,
    ) -> VisitorRequestTable | None:
        active_statuses = [
            RequestStatus.PENDING,
            RequestStatus.PROCESSING,
            RequestStatus.PENDING_APPROVAL,
            RequestStatus.ESCALATED,
        ]

        statement = (
            select(VisitorRequestTable)
            .where(
                VisitorRequestTable.email
                == email.lower(),
                VisitorRequestTable
                .request_type
                == request_type,
                VisitorRequestTable.status.in_(
                    active_statuses
                ),
            )
            .order_by(
                VisitorRequestTable
                .created_at
                .desc()
            )
            .limit(1)
        )

        return self.session.scalar(
            statement
        )

    def find_by_reference_for_session(
        self,
        *,
        reference: str,
        session_id: str,
    ) -> VisitorRequestTable | None:
        statement = (
            select(VisitorRequestTable)
            .join(
                ConsentGrantTable,
                VisitorRequestTable.consent_id
                == ConsentGrantTable.id,
            )
            .where(
                VisitorRequestTable.reference
                == reference,
                ConsentGrantTable.session_id
                == session_id,
            )
        )

        return self.session.scalar(
            statement
        )