from collections.abc import Callable
from datetime import date
from uuid import uuid4

from sqlalchemy.orm import Session

from youcode_guide.metier.helpers.article_processor import (
    process_knowledge_article,
)
from youcode_guide.metier.repositories.knowledge_article_repository import (
    KnowledgeArticleRepository,
)
from youcode_guide.metier.models.knowledge_article import KnowledgeArticle
from youcode_guide.metier.enums.knowledge_article_status import KnowledgeArticleStatus
from youcode_guide.database.sqlite.connection import (
    SessionFactory,
)


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


class KnowledgeArticleService:
    def __init__(
        self,
        *,
        session_factory: Callable[
            [],
            Session,
        ],
    ) -> None:
        self.session_factory = session_factory

    def create_draft(
        self,
        *,
        gap_id: int,
        title: str,
        content: str,
        category: str,
        created_by: str,
        source_name: str | None = None,
        valid_from: date | None = None,
        valid_until: date | None = None,
    ) -> KnowledgeArticle:
        self._validate_category(category)
        self._validate_actor(created_by)
        self._validate_validity(
            valid_from=valid_from,
            valid_until=valid_until,
        )

        processed = process_knowledge_article(
            title=title,
            content=content,
        )

        session = self.session_factory()

        try:
            repository = (
                KnowledgeArticleRepository(
                    session,
                )
            )

            article = repository.create(
                document_key=str(uuid4()),
                title=processed.title,
                content=processed.content,
                category=category,
                content_hash=(
                    processed.content_hash
                ),
                created_by=created_by.strip(),
                source_name=source_name,
            )

            if article.id is None:
                raise RuntimeError(
                    "Article ID was not generated."
                )

            repository.update_validity(
                article_id=article.id,
                valid_from=valid_from,
                valid_until=valid_until,
            )

            repository.link_to_gap(
                article_id=article.id,
                gap_id=gap_id,
            )

            session.commit()

            saved_article = (
                repository.get_by_id(article.id)
            )

            if saved_article is None:
                raise RuntimeError(
                    "Article could not be reloaded."
                )

            return saved_article

        except Exception:
            session.rollback()
            raise

        finally:
            session.close()

    def update_draft(
        self,
        *,
        article_id: int,
        title: str,
        content: str,
        category: str,
        source_name: str | None = None,
        valid_from: date | None = None,
        valid_until: date | None = None,
    ) -> KnowledgeArticle:
        self._validate_category(category)
        self._validate_validity(
            valid_from=valid_from,
            valid_until=valid_until,
        )

        processed = process_knowledge_article(
            title=title,
            content=content,
        )

        session = self.session_factory()

        try:
            repository = (
                KnowledgeArticleRepository(
                    session,
                )
            )

            current_article = (
                self._get_article_or_raise(
                    repository,
                    article_id,
                )
            )

            if (
                current_article.status
                != KnowledgeArticleStatus.DRAFT
            ):
                raise ValueError(
                    "Only draft articles "
                    "can be modified."
                )

            if (
                current_article.content_hash
                == processed.content_hash
                and current_article.category
                == category
                and current_article.source_name
                == source_name
                and current_article.valid_from
                == valid_from
                and current_article.valid_until
                == valid_until
            ):
                return current_article

            article = repository.update_content(
                article_id=article_id,
                title=processed.title,
                content=processed.content,
                category=category,
                content_hash=(
                    processed.content_hash
                ),
                source_name=source_name,
            )

            repository.update_validity(
                article_id=article_id,
                valid_from=valid_from,
                valid_until=valid_until,
            )

            session.commit()

            return article

        except Exception:
            session.rollback()
            raise

        finally:
            session.close()

    def submit_for_review(
        self,
        article_id: int,
    ) -> KnowledgeArticle:
        return self._transition(
            article_id=article_id,
            expected_status=(
                KnowledgeArticleStatus.DRAFT
            ),
            new_status=(
                KnowledgeArticleStatus.IN_REVIEW
            ),
        )

    def publish(
        self,
        *,
        article_id: int,
        reviewed_by: str,
    ) -> KnowledgeArticle:
        self._validate_actor(reviewed_by)

        return self._transition(
            article_id=article_id,
            expected_status=(
                KnowledgeArticleStatus.IN_REVIEW
            ),
            new_status=(
                KnowledgeArticleStatus.PUBLISHED
            ),
            reviewed_by=reviewed_by.strip(),
        )

    def reject(
        self,
        *,
        article_id: int,
        reviewed_by: str,
    ) -> KnowledgeArticle:
        self._validate_actor(reviewed_by)

        return self._transition(
            article_id=article_id,
            expected_status=(
                KnowledgeArticleStatus.IN_REVIEW
            ),
            new_status=(
                KnowledgeArticleStatus.REJECTED
            ),
            reviewed_by=reviewed_by.strip(),
        )

    def reopen(
        self,
        article_id: int,
    ) -> KnowledgeArticle:
        return self._transition(
            article_id=article_id,
            expected_status=(
                KnowledgeArticleStatus.REJECTED
            ),
            new_status=(
                KnowledgeArticleStatus.DRAFT
            ),
        )

    def archive(
        self,
        article_id: int,
    ) -> KnowledgeArticle:
        return self._transition(
            article_id=article_id,
            expected_status=(
                KnowledgeArticleStatus.PUBLISHED
            ),
            new_status=(
                KnowledgeArticleStatus.ARCHIVED
            ),
        )

    def get_by_id(
        self,
        article_id: int,
    ) -> KnowledgeArticle:
        session = self.session_factory()

        try:
            repository = (
                KnowledgeArticleRepository(
                    session,
                )
            )

            return self._get_article_or_raise(
                repository,
                article_id,
            )

        finally:
            session.close()

    def list_articles(
        self,
        *,
        status: (
            KnowledgeArticleStatus | None
        ) = None,
    ) -> list[KnowledgeArticle]:
        session = self.session_factory()

        try:
            repository = (
                KnowledgeArticleRepository(
                    session,
                )
            )

            if status is None:
                return repository.list_all()

            return repository.list_by_status(
                status,
            )

        finally:
            session.close()

    def _transition(
        self,
        *,
        article_id: int,
        expected_status: KnowledgeArticleStatus,
        new_status: KnowledgeArticleStatus,
        reviewed_by: str | None = None,
    ) -> KnowledgeArticle:
        session = self.session_factory()

        try:
            repository = (
                KnowledgeArticleRepository(
                    session,
                )
            )

            current_article = (
                self._get_article_or_raise(
                    repository,
                    article_id,
                )
            )

            if (
                current_article.status
                != expected_status
            ):
                raise ValueError(
                    "Invalid article transition: "
                    f"{current_article.status.value} "
                    f"→ {new_status.value}."
                )

            article = repository.update_status(
                article_id=article_id,
                status=new_status,
                reviewed_by=reviewed_by,
            )

            session.commit()

            return article

        except Exception:
            session.rollback()
            raise

        finally:
            session.close()

    @staticmethod
    def _get_article_or_raise(
        repository: (
            KnowledgeArticleRepository
        ),
        article_id: int,
    ) -> KnowledgeArticle:
        article = repository.get_by_id(
            article_id,
        )

        if article is None:
            raise ValueError(
                f"Knowledge article {article_id} "
                "not found."
            )

        return article

    @staticmethod
    def _validate_category(
        category: str,
    ) -> None:
        if category not in SUPPORTED_CATEGORIES:
            raise ValueError(
                f"Unsupported category: {category}"
            )

    @staticmethod
    def _validate_actor(
        actor: str,
    ) -> None:
        if not actor.strip():
            raise ValueError(
                "Administrator identifier "
                "is required."
            )

    @staticmethod
    def _validate_validity(
        *,
        valid_from: date | None,
        valid_until: date | None,
    ) -> None:
        if (
            valid_from is not None
            and valid_until is not None
            and valid_until < valid_from
        ):
            raise ValueError(
                "valid_until must be after "
                "valid_from."
            )
        



def create_knowledge_article_service(
) -> KnowledgeArticleService:
    return KnowledgeArticleService(
        session_factory=SessionFactory,
    )