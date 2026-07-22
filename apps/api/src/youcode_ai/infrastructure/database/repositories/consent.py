from sqlalchemy import select
from sqlalchemy.orm import Session

from youcode_ai.infrastructure.database.repositories.base import (
    BaseRepository,
)
from youcode_ai.infrastructure.database.tables import (
    ConsentGrantTable,
)


class ConsentRepository(
    BaseRepository[ConsentGrantTable]
):
    def __init__(
        self,
        *,
        session: Session,
    ) -> None:
        super().__init__(
            session=session,
            model_type=ConsentGrantTable,
        )

    def find_by_reference(
        self,
        reference: str,
    ) -> ConsentGrantTable | None:
        statement = select(
            ConsentGrantTable
        ).where(
            ConsentGrantTable.reference
            == reference
        )

        return self.session.scalar(
            statement
        )

    def find_by_token_hash(
        self,
        token_hash: str,
    ) -> ConsentGrantTable | None:
        statement = select(
            ConsentGrantTable
        ).where(
            ConsentGrantTable.token_hash
            == token_hash
        )

        return self.session.scalar(
            statement
        )