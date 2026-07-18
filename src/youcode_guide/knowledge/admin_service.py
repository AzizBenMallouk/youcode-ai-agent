from collections.abc import Callable

from sqlalchemy.orm import Session

from youcode_guide.knowledge.gap_repository import (
    KnowledgeGapRepository,
)
from youcode_guide.knowledge.models import (
    KnowledgeGap,
    KnowledgeGapDetails,
    KnowledgeGapStatus,
)
from youcode_guide.knowledge.question_repository import (
    KnowledgeGapQuestionRepository,
)
from youcode_guide.knowledge.semantic_store import (
    SemanticKnowledgeGapStore,
)


class KnowledgeGapAdminService:
    def __init__(
        self,
        *,
        session_factory: Callable[
            [],
            Session,
        ],
        semantic_store: (
            SemanticKnowledgeGapStore
        ),
    ) -> None:
        self.session_factory = session_factory
        self.semantic_store = semantic_store

    def list_gaps(
        self,
        *,
        status: (
            KnowledgeGapStatus | None
        ) = None,
        limit: int = 100,
    ) -> list[KnowledgeGap]:
        session = self.session_factory()

        try:
            repository = KnowledgeGapRepository(
                session,
            )

            if status is not None:
                return repository.list_by_status(
                    status,
                )[:limit]

            return repository.list_all(
                limit=limit,
            )

        finally:
            session.close()

    def get_details(
        self,
        gap_id: int,
    ) -> KnowledgeGapDetails:
        session = self.session_factory()

        try:
            gap_repository = (
                KnowledgeGapRepository(session)
            )

            question_repository = (
                KnowledgeGapQuestionRepository(
                    session,
                )
            )

            gap = gap_repository.get_by_id(
                gap_id,
            )

            if gap is None:
                raise ValueError(
                    f"Knowledge gap {gap_id} "
                    "not found."
                )

            questions = (
                question_repository
                .list_by_gap_id(gap_id)
            )

            return KnowledgeGapDetails(
                gap=gap,
                questions=questions,
            )

        finally:
            session.close()

    def start_review(
        self,
        gap_id: int,
    ) -> KnowledgeGap:
        return self._change_status(
            gap_id=gap_id,
            new_status=(
                KnowledgeGapStatus.IN_REVIEW
            ),
        )

    def reject(
        self,
        gap_id: int,
    ) -> KnowledgeGap:
        return self._change_status(
            gap_id=gap_id,
            new_status=(
                KnowledgeGapStatus.REJECTED
            ),
        )

    def reopen(
        self,
        gap_id: int,
    ) -> KnowledgeGap:
        return self._change_status(
            gap_id=gap_id,
            new_status=(
                KnowledgeGapStatus.PENDING
            ),
        )

    def _change_status(
        self,
        *,
        gap_id: int,
        new_status: KnowledgeGapStatus,
    ) -> KnowledgeGap:
        session = self.session_factory()

        try:
            repository = KnowledgeGapRepository(
                session,
            )

            current_gap = repository.get_by_id(
                gap_id,
            )

            if current_gap is None:
                raise ValueError(
                    f"Knowledge gap {gap_id} "
                    "not found."
                )

            updated_gap = (
                repository.update_status(
                    gap_id=gap_id,
                    status=new_status,
                )
            )

            if current_gap.vector_point_id:
                self.semantic_store.update_status(
                    vector_point_id=(
                        current_gap.vector_point_id
                    ),
                    status=new_status.value,
                )

            session.commit()

            return updated_gap

        except Exception:
            session.rollback()
            raise

        finally:
            session.close()