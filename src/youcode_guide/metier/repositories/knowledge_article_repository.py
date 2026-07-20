from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from youcode_guide.database.sqlite.schema.knowledge_article_table import KnowledgeArticleTable
from youcode_guide.database.sqlite.schema.knowledge_gap_article_table import KnowledgeGapArticleTable
from youcode_guide.database.sqlite.schema.knowledge_gap_table import KnowledgeGapTable

from youcode_guide.metier.models.kn import (
    KnowledgeArticle,
    KnowledgeArticleStatus,
)


class KnowledgeArticleRepository:
    def __init__(
        self,
        session: Session,
    ) -> None:
        self.session = session

    def create(
        self,
        *,
        document_key: str,
        title: str,
        content: str,
        category: str,
        content_hash: str,
        created_by: str,
        source_name: str | None = None,
    ) -> KnowledgeArticle:
        now = datetime.now(timezone.utc)

        table = KnowledgeArticleTable(
            document_key=document_key,
            title=title,
            content=content,
            category=category,
            status=(
                KnowledgeArticleStatus
                .DRAFT.value
            ),
            version=1,
            source_name=source_name,
            content_hash=content_hash,
            created_by=created_by,
            reviewed_by=None,
            valid_from=None,
            valid_until=None,
            created_at=now,
            updated_at=now,
            published_at=None,
            indexed_at=None,
        )

        self.session.add(table)
        self.session.flush()

        return self._to_model(table)

    def get_by_id(
        self,
        article_id: int,
    ) -> KnowledgeArticle | None:
        table = self.session.get(
            KnowledgeArticleTable,
            article_id,
        )

        if table is None:
            return None

        return self._to_model(table)

    def find_by_document_key(
        self,
        document_key: str,
    ) -> KnowledgeArticle | None:
        statement = (
            select(KnowledgeArticleTable)
            .where(
                KnowledgeArticleTable.document_key
                == document_key
            )
        )

        table = self.session.scalar(statement)

        if table is None:
            return None

        return self._to_model(table)

    def list_all(
        self,
        *,
        limit: int = 100,
    ) -> list[KnowledgeArticle]:
        statement = (
            select(KnowledgeArticleTable)
            .order_by(
                KnowledgeArticleTable
                .updated_at.desc()
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

    def list_by_status(
        self,
        status: KnowledgeArticleStatus,
        *,
        limit: int = 100,
    ) -> list[KnowledgeArticle]:
        statement = (
            select(KnowledgeArticleTable)
            .where(
                KnowledgeArticleTable.status
                == status.value
            )
            .order_by(
                KnowledgeArticleTable
                .updated_at.desc()
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

    def update_content(
        self,
        *,
        article_id: int,
        title: str,
        content: str,
        category: str,
        content_hash: str,
        source_name: str | None,
    ) -> KnowledgeArticle:
        table = self._get_table_or_raise(
            article_id,
        )

        table.title = title
        table.content = content
        table.category = category
        table.content_hash = content_hash
        table.source_name = source_name
        table.version += 1
        table.updated_at = datetime.now(
            timezone.utc,
        )

        # Une modification annule l'ancienne
        # indexation.
        table.indexed_at = None

        self.session.flush()

        return self._to_model(table)

    def update_status(
        self,
        *,
        article_id: int,
        status: KnowledgeArticleStatus,
        reviewed_by: str | None = None,
    ) -> KnowledgeArticle:
        table = self._get_table_or_raise(
            article_id,
        )

        table.status = status.value
        table.updated_at = datetime.now(
            timezone.utc,
        )

        if reviewed_by is not None:
            table.reviewed_by = reviewed_by

        if (
            status
            == KnowledgeArticleStatus.PUBLISHED
            and table.published_at is None
        ):
            table.published_at = datetime.now(
                timezone.utc,
            )

        self.session.flush()

        return self._to_model(table)

    def mark_as_indexed(
        self,
        article_id: int,
    ) -> KnowledgeArticle:
        table = self._get_table_or_raise(
            article_id,
        )

        table.indexed_at = datetime.now(
            timezone.utc,
        )

        self.session.flush()

        return self._to_model(table)

    def link_to_gap(
        self,
        *,
        article_id: int,
        gap_id: int,
    ) -> None:
        article = self.session.get(
            KnowledgeArticleTable,
            article_id,
        )

        if article is None:
            raise ValueError(
                f"Knowledge article {article_id} "
                "not found."
            )

        gap = self.session.get(
            KnowledgeGapTable,
            gap_id,
        )

        if gap is None:
            raise ValueError(
                f"Knowledge gap {gap_id} "
                "not found."
            )

        existing_link = self.session.get(
            KnowledgeGapArticleTable,
            (
                gap_id,
                article_id,
            ),
        )

        if existing_link is not None:
            return

        link = KnowledgeGapArticleTable(
            knowledge_gap_id=gap_id,
            knowledge_article_id=article_id,
            created_at=datetime.now(
                timezone.utc,
            ),
        )

        self.session.add(link)
        self.session.flush()

    def list_gap_ids(
        self,
        article_id: int,
    ) -> list[int]:
        statement = (
            select(
                KnowledgeGapArticleTable
                .knowledge_gap_id
            )
            .where(
                KnowledgeGapArticleTable
                .knowledge_article_id
                == article_id
            )
        )

        return list(
            self.session.scalars(
                statement,
            ).all()
        )

    def list_articles_for_gap(
        self,
        gap_id: int,
    ) -> list[KnowledgeArticle]:
        statement = (
            select(KnowledgeArticleTable)
            .join(
                KnowledgeGapArticleTable,
                KnowledgeGapArticleTable
                .knowledge_article_id
                == KnowledgeArticleTable.id,
            )
            .where(
                KnowledgeGapArticleTable
                .knowledge_gap_id
                == gap_id
            )
            .order_by(
                KnowledgeArticleTable
                .updated_at.desc()
            )
        )

        tables = self.session.scalars(
            statement,
        ).all()

        return [
            self._to_model(table)
            for table in tables
        ]

    def _get_table_or_raise(
        self,
        article_id: int,
    ) -> KnowledgeArticleTable:
        table = self.session.get(
            KnowledgeArticleTable,
            article_id,
        )

        if table is None:
            raise ValueError(
                f"Knowledge article {article_id} "
                "not found."
            )

        return table

    @staticmethod
    def _to_model(
        table: KnowledgeArticleTable,
    ) -> KnowledgeArticle:
        return KnowledgeArticle(
            id=table.id,
            document_key=table.document_key,
            title=table.title,
            content=table.content,
            category=table.category,
            status=KnowledgeArticleStatus(
                table.status
            ),
            version=table.version,
            source_name=table.source_name,
            content_hash=table.content_hash,
            created_by=table.created_by,
            reviewed_by=table.reviewed_by,
            valid_from=table.valid_from,
            valid_until=table.valid_until,
            created_at=table.created_at,
            updated_at=table.updated_at,
            published_at=table.published_at,
            indexed_at=table.indexed_at,
        )
    
    def update_validity(
        self,
        *,
        article_id: int,
        valid_from,
        valid_until,
    ) -> KnowledgeArticle:
        table = self._get_table_or_raise(
            article_id,
        )

        table.valid_from = valid_from
        table.valid_until = valid_until
        table.updated_at = datetime.now(
            timezone.utc,
        )

        self.session.flush()

        return self._to_model(table)
    
    