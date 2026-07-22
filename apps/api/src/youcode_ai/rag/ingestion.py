from dataclasses import dataclass
from uuid import (
    NAMESPACE_URL,
    uuid5,
)

from youcode_ai.core.config import (
    settings,
)
from youcode_ai.core.llm import (
    create_embedding_model,
)
from youcode_ai.infrastructure.vector import (
    get_qdrant_client,
)
from youcode_ai.rag.loaders import (
    load_text_documents,
)
from youcode_ai.rag.parent_store import (
    create_parent_document_store,
)
from youcode_ai.rag.splitter import (
    split_parent_child_documents,
)
from youcode_ai.rag.vector_store import (
    create_document_vector_store,
    recreate_document_collection,
)


@dataclass(frozen=True)
class IngestionResult:
    source_documents: int
    parent_chunks: int
    child_chunks: int
    indexed_children: int
    vector_size: int
    collection_name: str
    embedding_provider: str


class DocumentIngestionService:
    def run(self) -> IngestionResult:
        source_documents = (
            load_text_documents()
        )

        if not source_documents:
            raise ValueError(
                "No source documents were "
                "found."
            )

        split_result = (
            split_parent_child_documents(
                source_documents
            )
        )

        if not split_result.parents:
            raise ValueError(
                "No parent chunks were "
                "generated."
            )

        if not split_result.children:
            raise ValueError(
                "No child chunks were "
                "generated."
            )

        embeddings = (
            create_embedding_model()
        )

        client = get_qdrant_client()

        vector_size = (
            recreate_document_collection(
                client=client,
                embeddings=embeddings,
            )
        )

        vector_store = (
            create_document_vector_store(
                client=client,
                embeddings=embeddings,
            )
        )

        indexed_children = (
            self._index_children(
                vector_store=vector_store,
                children=(
                    split_result.children
                ),
            )
        )

        # Les parents sont remplacés uniquement
        # après la réussite de l'indexation.
        parent_store = (
            create_parent_document_store()
        )

        parent_store.replace_all(
            split_result.parents
        )

        return IngestionResult(
            source_documents=len(
                source_documents
            ),
            parent_chunks=len(
                split_result.parents
            ),
            child_chunks=len(
                split_result.children
            ),
            indexed_children=(
                indexed_children
            ),
            vector_size=vector_size,
            collection_name=(
                settings
                .qdrant_documents_collection
            ),
            embedding_provider=(
                settings.embedding_provider
            ),
        )

    def _index_children(
        self,
        *,
        vector_store,
        children,
    ) -> int:
        batch_size = (
            settings
            .rag_ingestion_batch_size
        )

        indexed_count = 0

        for start_index in range(
            0,
            len(children),
            batch_size,
        ):
            batch = children[
                start_index:
                start_index + batch_size
            ]

            point_ids = [
                self._create_point_id(
                    child.metadata[
                        "child_id"
                    ]
                )
                for child in batch
            ]

            vector_store.add_documents(
                documents=batch,
                ids=point_ids,
            )

            indexed_count += len(batch)

        return indexed_count

    @staticmethod
    def _create_point_id(
        child_id: str,
    ) -> str:
        """
        Qdrant accepte les UUID comme
        identifiants de points.
        """

        return str(
            uuid5(
                NAMESPACE_URL,
                child_id,
            )
        )