from dataclasses import dataclass

from langchain_core.documents import (
    Document,
)
from langchain_qdrant import (
    QdrantVectorStore,
)

from youcode_ai.core.config import (
    settings,
)
from youcode_ai.rag.parent_store import (
    ParentDocumentStore,
    create_parent_document_store,
)
from youcode_ai.rag.vector_store import (
    create_document_vector_store,
)


@dataclass(frozen=True)
class RetrievalResult:
    question: str
    children: list[Document]
    parents: list[Document]
    best_score: float | None

    @property
    def information_available(
        self,
    ) -> bool:
        return bool(
            self.children
            and self.parents
        )


class ParentChildRetriever:
    def __init__(
        self,
        *,
        vector_store: QdrantVectorStore,
        parent_store: ParentDocumentStore,
        top_k: int,
        score_threshold: float,
    ) -> None:
        self.vector_store = vector_store
        self.parent_store = parent_store
        self.top_k = top_k
        self.score_threshold = (
            score_threshold
        )

    def retrieve(
        self,
        question: str,
    ) -> RetrievalResult:
        normalized_question = (
            question.strip()
        )

        if not normalized_question:
            raise ValueError(
                "Retrieval question cannot "
                "be empty."
            )

        if not self.parent_store.exists():
            raise RuntimeError(
                "Parent document store does "
                "not exist. Run ingestion first."
            )

        scored_children = (
            self.vector_store
            .similarity_search_with_score(
                query=normalized_question,
                k=self.top_k,
            )
        )

        children: list[Document] = []

        parent_scores: dict[
            str,
            float,
        ] = {}

        parent_child_ids: dict[
            str,
            list[str],
        ] = {}

        for (
            child_document,
            score,
        ) in scored_children:
            normalized_score = float(score)

            if (
                normalized_score
                < self.score_threshold
            ):
                continue

            parent_id = (
                child_document.metadata.get(
                    "parent_id"
                )
            )

            child_id = (
                child_document.metadata.get(
                    "child_id"
                )
            )

            if not parent_id:
                continue

            child_metadata = {
                **child_document.metadata,
                "retrieval_score": (
                    normalized_score
                ),
            }

            children.append(
                Document(
                    page_content=(
                        child_document
                        .page_content
                    ),
                    metadata=child_metadata,
                )
            )

            current_parent_score = (
                parent_scores.get(
                    parent_id
                )
            )

            if (
                current_parent_score is None
                or normalized_score
                > current_parent_score
            ):
                parent_scores[
                    parent_id
                ] = normalized_score

            if child_id:
                parent_child_ids.setdefault(
                    parent_id,
                    [],
                ).append(child_id)

        ordered_parent_ids = sorted(
            parent_scores,
            key=lambda parent_id: (
                parent_scores[parent_id]
            ),
            reverse=True,
        )

        stored_parents = (
            self.parent_store.get_many(
                ordered_parent_ids
            )
        )

        parent_by_id = {
            parent.metadata["parent_id"]:
            parent
            for parent in stored_parents
            if parent.metadata.get(
                "parent_id"
            )
        }

        parents: list[Document] = []

        for parent_id in ordered_parent_ids:
            parent = parent_by_id.get(
                parent_id
            )

            if parent is None:
                continue

            parent_metadata = {
                **parent.metadata,
                "retrieval_score": (
                    parent_scores[
                        parent_id
                    ]
                ),
                "matched_child_ids": (
                    parent_child_ids.get(
                        parent_id,
                        [],
                    )
                ),
            }

            parents.append(
                Document(
                    page_content=(
                        parent.page_content
                    ),
                    metadata=parent_metadata,
                )
            )

        best_score = (
            max(parent_scores.values())
            if parent_scores
            else None
        )

        return RetrievalResult(
            question=normalized_question,
            children=children,
            parents=parents,
            best_score=best_score,
        )


def create_parent_child_retriever(
) -> ParentChildRetriever:
    vector_store = (
        create_document_vector_store()
    )

    parent_store = (
        create_parent_document_store()
    )

    return ParentChildRetriever(
        vector_store=vector_store,
        parent_store=parent_store,
        top_k=settings.rag_top_k,
        score_threshold=(
            settings.rag_score_threshold
        ),
    )