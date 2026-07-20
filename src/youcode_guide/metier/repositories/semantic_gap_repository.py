from uuid import NAMESPACE_URL, uuid5

from langchain_core.embeddings import Embeddings
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchAny,
    MatchValue,
    PointStruct,
    VectorParams,
)

from youcode_guide.metier.helpers.entity_extractor import (
    entities_are_compatible,
)
from youcode_guide.metier.models.knowledge_gap import KnowledgeGap
from youcode_guide.metier.models.semantic_knowledge_gap_match import SemanticKnowledgeGapMatch
from youcode_guide.config import settings
from youcode_guide.agents.shared.embeddings import (
    create_embedding_model,
)
from youcode_guide.database.vector.vector_store import (
    create_qdrant_client,
)

class SemanticKnowledgeGapRepository:
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
        if self.client.collection_exists(
            collection_name=self.collection_name,
        ):
            return

        probe_vector = self.embeddings.embed_query(
            "YouCode knowledge gap"
        )

        if not probe_vector:
            raise RuntimeError(
                "Embedding model returned "
                "an empty vector."
            )

        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(
                size=len(probe_vector),
                distance=Distance.COSINE,
            ),
        )

    def index_gap(
        self,
        gap: KnowledgeGap,
    ) -> str:
        if gap.id is None:
            raise ValueError(
                "Knowledge gap must have an ID "
                "before indexing."
            )

        self.initialize()

        point_id = self._create_point_id(
            gap.id
        )

        vector = self.embeddings.embed_query(
            gap.normalized_question
        )

        if not vector:
            raise RuntimeError(
                "Embedding model returned "
                "an empty vector."
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
                        "category": self._enum_value(
                            gap.category
                        ),
                        "language": self._enum_value(
                            gap.language
                        ),
                        "status": self._enum_value(
                            gap.status
                        ),
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
            normalized_question
        )

        if not query_vector:
            raise RuntimeError(
                "Embedding model returned "
                "an empty vector."
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
                    ),
                    FieldCondition(
                        key="status",
                        match=MatchAny(
                            any=[
                                "pending",
                                "in_review",
                            ]
                        ),
                    ),
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
                "knowledge_gap_id"
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
                status=str(
                    payload.get(
                        "status",
                        "pending",
                    )
                ),
                score=float(point.score),
            )

        return None

    def update_status(
        self,
        *,
        gap_id: int,
        status: str,
    ) -> None:
        self.initialize()

        self.client.set_payload(
            collection_name=self.collection_name,
            payload={
                "status": status,
            },
            points=[
                self._create_point_id(gap_id)
            ],
            wait=True,
        )

    def delete(
        self,
        gap_id: int,
    ) -> None:
        self.initialize()

        self.client.delete(
            collection_name=self.collection_name,
            points_selector=[
                self._create_point_id(gap_id)
            ],
            wait=True,
        )

    @staticmethod
    def _create_point_id(
        gap_id: int,
    ) -> str:
        return str(
            uuid5(
                NAMESPACE_URL,
                f"youcode-knowledge-gap:{gap_id}",
            )
        )

    @staticmethod
    def _enum_value(value: object) -> str:
        enum_value = getattr(
            value,
            "value",
            value,
        )

        return str(enum_value)
    


def create_semantic_knowledge_gap_repository(
) -> SemanticKnowledgeGapRepository:
    client = create_qdrant_client()
    embeddings = create_embedding_model()

    return SemanticKnowledgeGapRepository(
        client=client,
        embeddings=embeddings,
        collection_name=(
            settings
            .qdrant_knowledge_gap_collection
        ),
        similarity_threshold=(
            settings
            .knowledge_gap_similarity_threshold
        ),
    )