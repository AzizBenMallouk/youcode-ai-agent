from collections.abc import Callable
from uuid import uuid4

from sqlalchemy.orm import Session

from youcode_guide.knowledge.gap_repository import (
    KnowledgeGapRepository,
)
from youcode_guide.knowledge.models import (
    KnowledgeGap,
    KnowledgeGapMatchType,
    KnowledgeGapReportResult,
)
from youcode_guide.knowledge.processor import (
    ProcessedQuestion,
    process_question,
)
from youcode_guide.knowledge.question_repository import (
    KnowledgeGapQuestionRepository,
)
from youcode_guide.knowledge.semantic_store import (
    SemanticKnowledgeGapStore,
)


SUPPORTED_LANGUAGES = {
    "fr",
    "en",
    "ar",
    "darija",
}


SUPPORTED_CATEGORIES = {
    "general",
    "admission",
    "program",
    "campus",
    "pedagogy",
    "career",
    "event",
    "practical",
}


class KnowledgeGapService:
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

    def report(
        self,
        *,
        question: str,
        language: str,
        category: str,
    ) -> KnowledgeGapReportResult:
        self._validate_language(language)
        self._validate_category(category)

        processed = process_question(question)

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

            exact_question = (
                question_repository.find_by_hash(
                    processed.question_hash,
                )
            )

            if exact_question is not None:
                gap = (
                    gap_repository
                    .increment_occurrence(
                        exact_question
                        .knowledge_gap_id
                    )
                )

                session.commit()

                return KnowledgeGapReportResult(
                    gap=gap,
                    match_type=(
                        KnowledgeGapMatchType.EXACT
                    ),
                )

            semantic_match = (
                self.semantic_store.find_similar(
                    question=(
                        processed
                        .sanitized_question
                    ),
                    normalized_question=(
                        processed
                        .normalized_question
                    ),
                    category=category,
                )
            )

            if semantic_match is not None:
                existing_gap = (
                    gap_repository.get_by_id(
                        semantic_match
                        .knowledge_gap_id
                    )
                )

                if existing_gap is not None:
                    gap = self._attach_to_gap(
                        gap=existing_gap,
                        processed_question=processed,
                        language=language,
                        semantic_score=(
                            semantic_match.score
                        ),
                        gap_repository=(
                            gap_repository
                        ),
                        question_repository=(
                            question_repository
                        ),
                    )

                    session.commit()

                    return (
                        KnowledgeGapReportResult(
                            gap=gap,
                            match_type=(
                                KnowledgeGapMatchType
                                .SEMANTIC
                            ),
                            semantic_score=(
                                semantic_match.score
                            ),
                        )
                    )

                # Le point Qdrant existe mais son groupe
                # SQLite n'existe plus.
                self.semantic_store.delete(
                    semantic_match.vector_point_id,
                )

            result = self._create_new_gap(
                processed_question=processed,
                language=language,
                category=category,
                gap_repository=gap_repository,
                question_repository=(
                    question_repository
                ),
                session=session,
            )

            return result

        except Exception:
            session.rollback()
            raise

        finally:
            session.close()

    def _attach_to_gap(
        self,
        *,
        gap: KnowledgeGap,
        processed_question: ProcessedQuestion,
        language: str,
        semantic_score: float,
        gap_repository: (
            KnowledgeGapRepository
        ),
        question_repository: (
            KnowledgeGapQuestionRepository
        ),
    ) -> KnowledgeGap:
        if gap.id is None:
            raise RuntimeError(
                "Knowledge gap has no ID."
            )

        question_repository.create(
            knowledge_gap_id=gap.id,
            original_question=(
                processed_question
                .sanitized_question
            ),
            normalized_question=(
                processed_question
                .normalized_question
            ),
            question_hash=(
                processed_question.question_hash
            ),
            language=language,
            semantic_score=semantic_score,
        )

        return gap_repository.increment_occurrence(
            gap.id,
        )

    def _create_new_gap(
        self,
        *,
        processed_question: process_question,
        language: str,
        category: str,
        gap_repository: (
            KnowledgeGapRepository
        ),
        question_repository: (
            KnowledgeGapQuestionRepository
        ),
        session: Session,
    ) -> KnowledgeGapReportResult:
        vector_point_id = str(uuid4())

        gap = gap_repository.create(
            canonical_question=(
                processed_question
                .sanitized_question
            ),
            normalized_question=(
                processed_question
                .normalized_question
            ),
            language=language,
            category=category,
            vector_point_id=vector_point_id,
        )

        if gap.id is None:
            raise RuntimeError(
                "Knowledge gap ID was not generated."
            )

        question_repository.create(
            knowledge_gap_id=gap.id,
            original_question=(
                processed_question
                .sanitized_question
            ),
            normalized_question=(
                processed_question
                .normalized_question
            ),
            question_hash=(
                processed_question.question_hash
            ),
            language=language,
            semantic_score=1.0,
        )

        point_created = False

        try:
            self.semantic_store.index_gap(
                gap,
                vector_point_id=vector_point_id,
            )

            point_created = True

            gap_repository.mark_as_indexed(
                gap_id=gap.id,
                vector_point_id=vector_point_id,
            )

            session.commit()

        except Exception:
            session.rollback()

            if point_created:
                try:
                    self.semantic_store.delete(
                        vector_point_id,
                    )
                except Exception:
                    # Le nettoyage pourra être repris
                    # par une tâche de maintenance.
                    pass

            raise

        saved_gap = gap_repository.get_by_id(
            gap.id,
        )

        if saved_gap is None:
            raise RuntimeError(
                "Created knowledge gap "
                "could not be reloaded."
            )

        return KnowledgeGapReportResult(
            gap=saved_gap,
            match_type=(
                KnowledgeGapMatchType.CREATED
            ),
            semantic_score=None,
        )

    @staticmethod
    def _validate_language(
        language: str,
    ) -> None:
        if language not in SUPPORTED_LANGUAGES:
            raise ValueError(
                f"Unsupported language: {language}"
            )

    @staticmethod
    def _validate_category(
        category: str,
    ) -> None:
        if category not in SUPPORTED_CATEGORIES:
            raise ValueError(
                f"Unsupported category: {category}"
            )