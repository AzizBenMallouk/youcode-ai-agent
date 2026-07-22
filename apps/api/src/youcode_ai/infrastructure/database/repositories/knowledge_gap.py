from sqlalchemy import select
from sqlalchemy.orm import (
    Session,
    selectinload,
)

from youcode_ai.domain.enums import (
    KnowledgeGapStatus,
)
from youcode_ai.infrastructure.database.repositories.base import (
    BaseRepository,
)
from youcode_ai.infrastructure.database.tables import (
    KnowledgeGapTable,
)


class KnowledgeGapRepository(
    BaseRepository[KnowledgeGapTable]
):
    def __init__(
        self,
        *,
        session: Session,
    ) -> None:
        super().__init__(
            session=session,
            model_type=KnowledgeGapTable,
        )

    def find_by_id_with_details(
        self,
        gap_id: str,
    ) -> KnowledgeGapTable | None:
        statement = (
            select(KnowledgeGapTable)
            .options(
                selectinload(
                    KnowledgeGapTable
                    .questions
                ),
                selectinload(
                    KnowledgeGapTable
                    .answers
                ),
            )
            .where(
                KnowledgeGapTable.id
                == gap_id
            )
        )

        return self.session.scalar(
            statement
        )

    def list_by_status(
        self,
        *,
        status: KnowledgeGapStatus,
        limit: int = 100,
        offset: int = 0,
    ) -> list[KnowledgeGapTable]:
        statement = (
            select(KnowledgeGapTable)
            .where(
                KnowledgeGapTable.status
                == status
            )
            .order_by(
                KnowledgeGapTable
                .occurrence_count
                .desc(),
                KnowledgeGapTable
                .created_at
                .asc(),
            )
            .offset(offset)
            .limit(limit)
        )

        return list(
            self.session.scalars(
                statement
            ).all()
        )

    def find_by_vector_point_id(
        self,
        vector_point_id: str,
    ) -> KnowledgeGapTable | None:
        statement = select(
            KnowledgeGapTable
        ).where(
            KnowledgeGapTable.vector_point_id
            == vector_point_id
        )

        return self.session.scalar(
            statement
        )