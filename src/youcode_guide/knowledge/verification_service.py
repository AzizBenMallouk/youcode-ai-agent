import math
from collections.abc import Callable

from sqlalchemy.orm import Session

from youcode_guide.knowledge.article_repository import (
    KnowledgeArticleRepository,
)
from youcode_guide.knowledge.gap_repository import (
    KnowledgeGapRepository,
)
from youcode_guide.knowledge.models import (
    KnowledgeArticleStatus,
    KnowledgeArticleVerificationResult,
    KnowledgeGapQuestionVerification,
    KnowledgeGapStatus,
    KnowledgeGapVerificationResult,
)
from youcode_guide.knowledge.question_repository import (
    KnowledgeGapQuestionRepository,
)
from youcode_guide.knowledge.semantic_store import (
    SemanticKnowledgeGapStore,
)
from youcode_guide.rag.retriever import (
    ParentChildRetriever,
)


class KnowledgeGapVerificationService:
    def __init__(
        self,
        *,
        session_factory: Callable[
            [],
            Session,
        ],
        retriever: ParentChildRetriever,
        semantic_store: (
            SemanticKnowledgeGapStore
        ),
        minimum_coverage: float = 0.60,
    ) -> None:
        if not 0 < minimum_coverage <= 1:
            raise ValueError(
                "minimum_coverage must be "
                "between 0 and 1."
            )

        self.session_factory = session_factory
        self.retriever = retriever
        self.semantic_store = semantic_store
        self.minimum_coverage = (
            minimum_coverage
        )

    def verify_article(
        self,
        article_id: int,
    ) -> KnowledgeArticleVerificationResult:
        session = self.session_factory()

        try:
            article_repository = (
                KnowledgeArticleRepository(
                    session,
                )
            )

            gap_repository = (
                KnowledgeGapRepository(session)
            )

            question_repository = (
                KnowledgeGapQuestionRepository(
                    session,
                )
            )

            article = (
                article_repository.get_by_id(
                    article_id,
                )
            )

            if article is None:
                raise ValueError(
                    f"Knowledge article "
                    f"{article_id} not found."
                )

            if (
                article.status
                != KnowledgeArticleStatus
                .PUBLISHED
            ):
                raise ValueError(
                    "Only published articles "
                    "can be verified."
                )

            if article.indexed_at is None:
                raise ValueError(
                    "Article must be indexed "
                    "before verification."
                )

            gap_ids = (
                article_repository.list_gap_ids(
                    article_id,
                )
            )

            gap_results: list[
                KnowledgeGapVerificationResult
            ] = []

            for gap_id in gap_ids:
                result = self._verify_gap(
                    article_id=article_id,
                    gap_id=gap_id,
                    gap_repository=(
                        gap_repository
                    ),
                    question_repository=(
                        question_repository
                    ),
                )

                gap_results.append(result)

            session.commit()

            return (
                KnowledgeArticleVerificationResult(
                    article_id=article_id,
                    gap_results=gap_results,
                )
            )

        except Exception:
            session.rollback()
            raise

        finally:
            session.close()

    def _verify_gap(
        self,
        *,
        article_id: int,
        gap_id: int,
        gap_repository: (
            KnowledgeGapRepository
        ),
        question_repository: (
            KnowledgeGapQuestionRepository
        ),
    ) -> KnowledgeGapVerificationResult:
        gap = gap_repository.get_by_id(
            gap_id,
        )

        if gap is None:
            raise ValueError(
                f"Knowledge gap {gap_id} "
                "not found."
            )

        questions = (
            question_repository.list_by_gap_id(
                gap_id,
            )
        )

        if not questions:
            raise ValueError(
                f"Knowledge gap {gap_id} "
                "has no questions."
            )

        verification_results: list[
            KnowledgeGapQuestionVerification
        ] = []

        for question in questions:
            retrieval_result = (
                self.retriever.invoke(
                    question.original_question
                )
            )

            article_found = any(
                parent.metadata.get(
                    "article_id"
                )
                == article_id
                for parent
                in retrieval_result.parents
            )

            verification_results.append(
                KnowledgeGapQuestionVerification(
                    question_id=question.id,
                    question=(
                        question.original_question
                    ),
                    article_found=article_found,
                    retrieved_parent_count=len(
                        retrieval_result.parents
                    ),
                )
            )

        matched_questions = sum(
            1
            for result in verification_results
            if result.article_found
        )

        total_questions = len(
            verification_results
        )

        coverage = (
            matched_questions
            / total_questions
        )

        minimum_matches = math.ceil(
            total_questions
            * self.minimum_coverage
        )

        resolved = (
            matched_questions
            >= minimum_matches
        )

        new_status = (
            KnowledgeGapStatus.RESOLVED
            if resolved
            else KnowledgeGapStatus.IN_REVIEW
        )

        gap_repository.update_status(
            gap_id=gap_id,
            status=new_status,
        )

        if gap.vector_point_id:
            self.semantic_store.update_status(
                vector_point_id=(
                    gap.vector_point_id
                ),
                status=new_status.value,
            )

        return KnowledgeGapVerificationResult(
            gap_id=gap_id,
            article_id=article_id,
            resolved=resolved,
            matched_questions=(
                matched_questions
            ),
            total_questions=total_questions,
            coverage=coverage,
            questions=verification_results,
        )