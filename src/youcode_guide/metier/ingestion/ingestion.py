from uuid import NAMESPACE_URL, uuid5

from youcode_guide.config import settings
from youcode_guide.agents.shared.embeddings import (
    create_embedding_model,
)
from youcode_guide.metier.ingestion.loaders import (
    load_text_documents,
)
from youcode_guide.metier.ingestion.parent_store import (
    ParentDocumentStore,
)
from youcode_guide.metier.ingestion.splitter import (
    split_parent_child_documents,
)
from youcode_guide.database.vector.vector_store import (
    create_qdrant_client,
    create_vector_store,
    recreate_collection,
)


class IngestionService:
    def run(self) -> dict:
        source_documents = load_text_documents(
            settings.documents_path
        )

        if not source_documents:
            raise ValueError(
                "No source documents were found."
            )

        split_result = (
            split_parent_child_documents(
                source_documents
            )
        )

        if not split_result.children:
            raise ValueError(
                "No child chunks were generated."
            )

        parent_store = ParentDocumentStore(
            settings.parent_store_path
        )

        parent_store.replace_all(
            split_result.parents
        )

        embedding_model = (
            create_embedding_model()
        )

        client = create_qdrant_client()

        vector_size = recreate_collection(
            client=client,
            embedding_model=embedding_model,
        ) # ERROR

        vector_store = create_vector_store(
            client=client,
            embedding_model=embedding_model,
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

        vector_store.add_documents(
            documents=split_result.children,
            ids=child_ids,
        )

        return {
            "source_documents": len(
                source_documents
            ),
            "parent_chunks": len(
                split_result.parents
            ),
            "child_chunks": len(
                split_result.children
            ),
            "vector_size": vector_size,
            "collection": (
                settings.qdrant_collection
            ),
        }