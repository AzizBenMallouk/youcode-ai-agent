from collections.abc import Callable
from datetime import date
from uuid import NAMESPACE_URL, uuid5
from youcode_guide.config import settings
from langchain_qdrant import (
    QdrantVectorStore,
)
from qdrant_client import QdrantClient
from sqlalchemy.orm import Session

from youcode_guide.metier.mapper.article_document import (
    article_to_document,
)
from youcode_guide.metier.repositories.knowledge_article_repository import (
    KnowledgeArticleRepository,
)
from youcode_guide.metier.models.knowledge_article import KnowledgeArticle
from youcode_guide.metier.enums.knowledge_article_status import KnowledgeArticleStatus

from youcode_guide.metier.ingestion.parent_store import (
    ParentDocumentStore,
)
from youcode_guide.metier.ingestion.splitter import (
    split_parent_child_documents,
)
from youcode_guide.database.vector.document_store import (
    delete_document_vectors,
)
from youcode_guide.database.sqlite.connection import (
    SessionFactory,
)
from youcode_guide.agent.llm.embeddings import create_embedding_model
from youcode_guide.database.vector.vector_store import create_qdrant_client
from youcode_guide.database.vector.document_store import create_document_vector_store

class KnowledgeArticleIngestionService:
    def __init__(
        self,
        *,
        session_factory: Callable[
            [],
            Session,
        ],
        client: QdrantClient,
        vector_store: QdrantVectorStore,
        parent_store: ParentDocumentStore,
    ) -> None:
        self.session_factory = session_factory
        self.client = client
        self.vector_store = vector_store
        self.parent_store = parent_store

    def ingest(
        self,
        article_id: int,
    ) -> dict:
        session = self.session_factory()

        try:
            repository = (
                KnowledgeArticleRepository(
                    session,
                )
            )

            article = repository.get_by_id(
                article_id,
            )

            if article is None:
                raise ValueError(
                    f"Knowledge article "
                    f"{article_id} not found."
                )

            self._validate_article(article)

            gap_ids = repository.list_gap_ids(
                article_id,
            )

            source_document = (
                article_to_document(
                    article,
                    gap_ids=gap_ids,
                )
            )

            document_id = (
                source_document.metadata[
                    "document_id"
                ]
            )

            split_result = (
                split_parent_child_documents(
                    [source_document]
                )
            )

            if not split_result.parents:
                raise ValueError(
                    "No parent chunks "
                    "were generated."
                )

            if not split_result.children:
                raise ValueError(
                    "No child chunks "
                    "were generated."
                )

            # Supprimer seulement l'ancienne version
            # de cet article.
            delete_document_vectors(
                client=self.client,
                document_id=document_id,
            )

            self.parent_store.replace_document(
                document_id=document_id,
                documents=split_result.parents,
            )

            child_ids = [
                str(
                    uuid5(
                        NAMESPACE_URL,
                        child.metadata["child_id"],
                    )
                )
                for child in split_result.children
            ]

            self.vector_store.add_documents(
                documents=(
                    split_result.children
                ),
                ids=child_ids,
            )

            indexed_article = (
                repository.mark_as_indexed(
                    article_id
                )
            )

            session.commit()

            return {
                "article_id": article_id,
                "document_id": document_id,
                "version": (
                    indexed_article.version
                ),
                "parent_chunks": len(
                    split_result.parents
                ),
                "child_chunks": len(
                    split_result.children
                ),
                "gap_ids": gap_ids,
                "indexed_at": (
                    indexed_article
                    .indexed_at
                    .isoformat()
                    if indexed_article
                    .indexed_at
                    else None
                ),
            }

        except Exception:
            session.rollback()
            raise

        finally:
            session.close()

    @staticmethod
    def _validate_article(
        article: KnowledgeArticle,
    ) -> None:
        if (
            article.status
            != KnowledgeArticleStatus.PUBLISHED
        ):
            raise ValueError(
                "Only published articles "
                "can be indexed."
            )

        today = date.today()

        if (
            article.valid_from is not None
            and article.valid_from > today
        ):
            raise ValueError(
                "Article is not valid yet."
            )

        if (
            article.valid_until is not None
            and article.valid_until < today
        ):
            raise ValueError(
                "Article has expired."
            )
        



def create_article_ingestion_service(
) -> KnowledgeArticleIngestionService:
    embedding_model = (
        create_embedding_model()
    )

    client = create_qdrant_client()

    vector_store = create_document_vector_store(
        client=client,
        embeddings=embedding_model,
    )

    parent_store = ParentDocumentStore(
        settings.parent_store_path,
    )

    return KnowledgeArticleIngestionService(
        session_factory=SessionFactory,
        client=client,
        vector_store=vector_store,
        parent_store=parent_store,
    )
