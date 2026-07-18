from qdrant_client import QdrantClient

from youcode_guide.config import settings
from youcode_guide.knowledge.semantic_store import (
    SemanticKnowledgeGapStore,
)
from youcode_guide.rag.embeddings import (
    create_embedding_model,
)
from youcode_guide.database.connection import (
    SessionFactory,
)
from youcode_guide.knowledge.service import (
    KnowledgeGapService,
)
from youcode_guide.rag.vector_store import (
    create_qdrant_client
)
from youcode_guide.knowledge.admin_service import (
    KnowledgeGapAdminService,
)

def create_semantic_knowledge_gap_store(
) -> SemanticKnowledgeGapStore:
    client = create_qdrant_client()

    embeddings = create_embedding_model()

    return SemanticKnowledgeGapStore(
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



def create_knowledge_gap_service(
) -> KnowledgeGapService:
    semantic_store = (
        create_semantic_knowledge_gap_store()
    )

    return KnowledgeGapService(
        session_factory=SessionFactory,
        semantic_store=semantic_store,
    )



def create_knowledge_gap_admin_service(
) -> KnowledgeGapAdminService:
    semantic_store = (
        create_semantic_knowledge_gap_store()
    )

    return KnowledgeGapAdminService(
        session_factory=SessionFactory,
        semantic_store=semantic_store,
    )