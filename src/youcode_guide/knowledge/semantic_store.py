import logging
from uuid import uuid4

from langchain_core.embeddings import Embeddings
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointStruct,
    VectorParams,
)

from youcode_guide.knowledge.entity_extractor import (
    entities_are_compatible,
)
from youcode_guide.knowledge.models import (
    KnowledgeGap,
    SemanticKnowledgeGapMatch,
)



class SemanticKnowledgeGapStore:
    def __init__(
        self,
        *,
        client: QdrantClient,
        embeddings: Embeddings,
        collection_name: str,
        similarity_threshold: float,
    ) -> None:
        self.client = client
        self.embeddings = embeddings
        self.collection_name = collection_name
        self.similarity_threshold = (
            similarity_threshold
        )

    def initialize(self) -> None:
        """
        Crée la collection uniquement si elle
        n'existe pas encore.
        """

        if self.client.collection_exists(
            collection_name=self.collection_name,
        ):
            return

        probe_vector = self.embeddings.embed_query(
            "YouCode knowledge gap"
        )

        vector_size = len(probe_vector)

        if vector_size == 0:
            raise RuntimeError(
                "Embedding model returned "
                "an empty vector."
            )

        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(
                size=vector_size,
                distance=Distance.COSINE,
            ),
        )

    def index_gap(
        self,
        gap: KnowledgeGap,
        *,
        vector_point_id: str | None = None,
    ) -> str:
        if gap.id is None:
            raise ValueError(
                "Knowledge gap must have an ID "
                "before indexing."
            )

        self.initialize()

        point_id = (
            vector_point_id
            or str(uuid4())
        )

        vector = self.embeddings.embed_query(
            gap.normalized_question,
        )

        self.client.upsert(
            collection_name=self.collection_name,
            points=[
                PointStruct(
                    id=point_id,
                    vector=vector,
                    payload={
                        "knowledge_gap_id": gap.id,
                        "canonical_question": (
                            gap.canonical_question
                        ),
                        "normalized_question": (
                            gap.normalized_question
                        ),
                        "category": gap.category,
                        "language": gap.language,
                        "status": gap.status.value,
                    },
                )
            ],
            wait=True,
        )

        return point_id

    def find_similar(
        self,
        *,
        question: str,
        normalized_question: str,
        category: str,
        limit: int = 5,
    ) -> SemanticKnowledgeGapMatch | None:
        self.initialize()

        query_vector = self.embeddings.embed_query(
            normalized_question,
        )

        response = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            query_filter=Filter(
                must=[
                    FieldCondition(
                        key="category",
                        match=MatchValue(
                            value=category,
                        ),
                    )
                ]
            ),
            limit=limit,
            score_threshold=(
                self.similarity_threshold
            ),
            with_payload=True,
        )

        for point in response.points:
            payload = point.payload or {}

            status = str(
                payload.get(
                    "status",
                    "pending",
                )
            )

            if status not in {
                "pending",
                "in_review",
            }:
                continue

            canonical_question = str(
                payload.get(
                    "canonical_question",
                    "",
                )
            )

            if not canonical_question:
                continue

            if not entities_are_compatible(
                question,
                canonical_question,
            ):
                continue

            gap_id = payload.get(
                "knowledge_gap_id",
            )

            if not isinstance(gap_id, int):
                continue

            return SemanticKnowledgeGapMatch(
                knowledge_gap_id=gap_id,
                vector_point_id=str(point.id),
                canonical_question=(
                    canonical_question
                ),
                category=str(
                    payload.get(
                        "category",
                        category,
                    )
                ),
                status=status,
                score=float(point.score),
            )

        return None

    def update_status(
        self,
        *,
        vector_point_id: str,
        status: str,
    ) -> None:
        self.client.set_payload(
            collection_name=self.collection_name,
            payload={
                "status": status,
            },
            points=[
                vector_point_id,
            ],
            wait=True,
        )

    def delete(
        self,
        vector_point_id: str,
    ) -> None:
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=[
                vector_point_id,
            ],
            wait=True,
        )