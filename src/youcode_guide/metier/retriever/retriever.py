from dataclasses import dataclass

from langchain_core.documents import Document
from langchain_qdrant import QdrantVectorStore

from youcode_guide.config import settings
from youcode_guide.agents.shared.embeddings import (
    create_embedding_model,
)
from youcode_guide.metier.ingestion.parent_store import (
    ParentDocumentStore,
)
from youcode_guide.database.vector.vector_store import (
    create_qdrant_client
)
from youcode_guide.database.vector.document_store import (
    create_document_vector_store
)



@dataclass
class RetrievalResult:
    children: list[Document]
    parents: list[Document]

    @property
    def information_available(self) -> bool:
        return bool(self.parents)

    @property
    def child_count(self) -> int:
        return len(self.children)

    @property
    def parent_count(self) -> int:
        return len(self.parents)


class ParentChildRetriever:
    def __init__(
        self,
        vector_store: QdrantVectorStore,
        parent_store: ParentDocumentStore,
        top_k: int = 5,
        score_threshold: float = 0.55,
    ) -> None:
        self.vector_store = vector_store
        self.parent_store = parent_store
        self.top_k = top_k
        self.score_threshold = score_threshold

    def invoke(
        self,
        question: str,
    ) -> RetrievalResult:
        clean_question = question.strip()

        if not clean_question:
            return RetrievalResult(
                children=[],
                parents=[],
            )

        results = (
            self.vector_store
            .similarity_search_with_relevance_scores(
                query=clean_question,
                k=self.top_k,
            )
        )

        relevant_children: list[Document] = []
        parent_scores: dict[str, float] = {}
        parent_child_ids: dict[str, list[str]] = {}

        for child, score in results:
            if score < self.score_threshold:
                continue

            parent_id = child.metadata.get(
                "parent_id"
            )

            if not parent_id:
                continue

            child.metadata["relevance_score"] = (
                float(score)
            )

            relevant_children.append(child)

            previous_score = parent_scores.get(
                parent_id,
                0.0,
            )

            parent_scores[parent_id] = max(
                previous_score,
                float(score),
            )

            child_id = child.metadata.get(
                "child_id"
            )

            if child_id:
                parent_child_ids.setdefault(
                    parent_id,
                    [],
                ).append(child_id)

        ordered_parent_ids = sorted(
            parent_scores,
            key=parent_scores.get,
            reverse=True,
        )

        parents = self.parent_store.get_many(
            ordered_parent_ids
        )

        for parent in parents:
            parent_id = parent.metadata[
                "parent_id"
            ]

            parent.metadata["relevance_score"] = (
                parent_scores[parent_id]
            )

            parent.metadata["matched_child_ids"] = (
                parent_child_ids.get(
                    parent_id,
                    [],
                )
            )

        return RetrievalResult(
            children=relevant_children,
            parents=parents,
        )
    
    
def create_parent_child_retriever(
) -> ParentChildRetriever:
    embedding_model = create_embedding_model()

    client = create_qdrant_client()

    vector_store = create_document_vector_store(
        client=client,
        embeddings=embedding_model,
    )

    parent_store = ParentDocumentStore(
        settings.parent_store_path
    )

    return ParentChildRetriever(
        vector_store=vector_store,
        parent_store=parent_store,
        top_k=settings.rag_top_k,
        score_threshold=(
            settings.rag_score_threshold
        ),
    )