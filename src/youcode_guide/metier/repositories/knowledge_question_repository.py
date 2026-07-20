from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from youcode_guide.database.sqlite.schema.knowledge_gap_question_table import (
    KnowledgeGapQuestionTable,
)
from youcode_guide.metier.models.knowledge_gap_question import (
    KnowledgeGapQuestion,
)


class KnowledgeGapQuestionRepository:
    def __init__(
        self,
        session: Session,
    ) -> None:
        self.session = session

    def create(
        self,
        *,
        knowledge_gap_id: int,
        original_question: str,
        normalized_question: str,
        question_hash: str,
        language: str,
        semantic_score: float | None = None,
    ) -> KnowledgeGapQuestion:
        table = KnowledgeGapQuestionTable(
            knowledge_gap_id=knowledge_gap_id,
            original_question=original_question,
            normalized_question=(
                normalized_question
            ),
            question_hash=question_hash,
            language=language,
            semantic_score=semantic_score,
            created_at=datetime.now(
                timezone.utc,
            ),
        )

        self.session.add(table)
        self.session.flush()

        return self._to_model(table)

    def get_by_id(
        self,
        question_id: int,
    ) -> KnowledgeGapQuestion | None:
        table = self.session.get(
            KnowledgeGapQuestionTable,
            question_id,
        )

        if table is None:
            return None

        return self._to_model(table)

    def find_by_hash(
        self,
        question_hash: str,
    ) -> KnowledgeGapQuestion | None:
        statement = (
            select(KnowledgeGapQuestionTable)
            .where(
                KnowledgeGapQuestionTable
                .question_hash
                == question_hash
            )
        )

        table = self.session.scalar(statement)

        if table is None:
            return None

        return self._to_model(table)

    def list_by_gap_id(
        self,
        knowledge_gap_id: int,
    ) -> list[KnowledgeGapQuestion]:
        statement = (
            select(KnowledgeGapQuestionTable)
            .where(
                KnowledgeGapQuestionTable
                .knowledge_gap_id
                == knowledge_gap_id
            )
            .order_by(
                KnowledgeGapQuestionTable
                .created_at.asc()
            )
        )

        tables = self.session.scalars(
            statement,
        ).all()

        return [
            self._to_model(table)
            for table in tables
        ]

    def count_by_gap_id(
        self,
        knowledge_gap_id: int,
    ) -> int:
        return len(
            self.list_by_gap_id(
                knowledge_gap_id,
            )
        )

    @staticmethod
    def _to_model(
        table: KnowledgeGapQuestionTable,
    ) -> KnowledgeGapQuestion:
        return KnowledgeGapQuestion(
            id=table.id,
            knowledge_gap_id=(
                table.knowledge_gap_id
            ),
            original_question=(
                table.original_question
            ),
            normalized_question=(
                table.normalized_question
            ),
            question_hash=(
                table.question_hash
            ),
            language=table.language,
            semantic_score=(
                table.semantic_score
            ),
            created_at=table.created_at,
        )