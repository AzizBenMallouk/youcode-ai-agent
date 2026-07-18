from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from youcode_guide.database.schema import (
    KnowledgeGapTable,
)
from youcode_guide.knowledge.models import (
    KnowledgeGap,
    KnowledgeGapStatus,
)


class KnowledgeGapRepository:
    def __init__(
        self,
        session: Session,
    ) -> None:
        self.session = session

    def create(
        self,
        *,
        canonical_question: str,
        normalized_question: str,
        language: str,
        category: str,
        vector_point_id: str | None = None,
    ) -> KnowledgeGap:
        now = datetime.now(timezone.utc)

        table = KnowledgeGapTable(
            canonical_question=canonical_question,
            normalized_question=normalized_question,
            language=language,
            category=category,
            occurrence_count=1,
            status=KnowledgeGapStatus.PENDING.value,
            vector_point_id=vector_point_id,
            created_at=now,
            last_asked_at=now,
            resolved_at=None,
            indexed_at=None,
        )

        self.session.add(table)

        # Exécute l'INSERT sans commit afin d'obtenir l'id.
        self.session.flush()

        return self._to_model(table)

    def get_by_id(
        self,
        gap_id: int,
    ) -> KnowledgeGap | None:
        table = self.session.get(
            KnowledgeGapTable,
            gap_id,
        )

        if table is None:
            return None

        return self._to_model(table)

    def list_by_status(
        self,
        status: KnowledgeGapStatus,
    ) -> list[KnowledgeGap]:
        statement = (
            select(KnowledgeGapTable)
            .where(
                KnowledgeGapTable.status
                == status.value
            )
            .order_by(
                KnowledgeGapTable
                .occurrence_count.desc(),
                KnowledgeGapTable
                .last_asked_at.desc(),
            )
        )

        tables = self.session.scalars(
            statement,
        ).all()

        return [
            self._to_model(table)
            for table in tables
        ]

    def increment_occurrence(
        self,
        gap_id: int,
    ) -> KnowledgeGap:
        table = self.session.get(
            KnowledgeGapTable,
            gap_id,
        )

        if table is None:
            raise ValueError(
                f"Knowledge gap {gap_id} not found."
            )

        table.occurrence_count += 1
        table.last_asked_at = datetime.now(
            timezone.utc,
        )

        self.session.flush()

        return self._to_model(table)

    def update_status(
        self,
        *,
        gap_id: int,
        status: KnowledgeGapStatus,
    ) -> KnowledgeGap:
        table = self.session.get(
            KnowledgeGapTable,
            gap_id,
        )

        if table is None:
            raise ValueError(
                f"Knowledge gap {gap_id} not found."
            )

        table.status = status.value

        if status == KnowledgeGapStatus.RESOLVED:
            table.resolved_at = datetime.now(
                timezone.utc,
            )
        else:
            table.resolved_at = None

        self.session.flush()

        return self._to_model(table)

    def mark_as_indexed(
        self,
        *,
        gap_id: int,
        vector_point_id: str,
    ) -> KnowledgeGap:
        table = self.session.get(
            KnowledgeGapTable,
            gap_id,
        )

        if table is None:
            raise ValueError(
                f"Knowledge gap {gap_id} not found."
            )

        table.vector_point_id = vector_point_id
        table.indexed_at = datetime.now(
            timezone.utc,
        )

        self.session.flush()

        return self._to_model(table)

    @staticmethod
    def _to_model(
        table: KnowledgeGapTable,
    ) -> KnowledgeGap:
        return KnowledgeGap(
            id=table.id,
            canonical_question=(
                table.canonical_question
            ),
            normalized_question=(
                table.normalized_question
            ),
            language=table.language,
            category=table.category,
            occurrence_count=table.occurrence_count,
            status=KnowledgeGapStatus(
                table.status
            ),
            created_at=table.created_at,
            last_asked_at=table.last_asked_at,
            resolved_at=table.resolved_at,
            vector_point_id=table.vector_point_id,
            indexed_at=table.indexed_at,
        )
    

    def list_all(
        self,
        *,
        limit: int = 100,
    ) -> list[KnowledgeGap]:
        statement = (
            select(KnowledgeGapTable)
            .order_by(
                KnowledgeGapTable
                .occurrence_count.desc(),
                KnowledgeGapTable
                .last_asked_at.desc(),
            )
            .limit(limit)
        )

        tables = self.session.scalars(
            statement,
        ).all()

        return [
            self._to_model(table)
            for table in tables
        ]