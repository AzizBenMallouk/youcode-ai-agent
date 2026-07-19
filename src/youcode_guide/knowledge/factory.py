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
    create_qdrant_client,
    create_vector_store,
)
from youcode_guide.knowledge.admin_service import (
    KnowledgeGapAdminService,
)
from youcode_guide.knowledge.article_service import (
    KnowledgeArticleService,
)
from youcode_guide.knowledge.article_ingestion_service import (
    KnowledgeArticleIngestionService,
)
from youcode_guide.rag.parent_store import (
    ParentDocumentStore,
)
from youcode_guide.knowledge.verification_service import (
    KnowledgeGapVerificationService,
)
from youcode_guide.rag.retriever import (
    create_parent_child_retriever,
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


def create_knowledge_article_service(
) -> KnowledgeArticleService:
    return KnowledgeArticleService(
        session_factory=SessionFactory,
    )

def create_article_ingestion_service(
) -> KnowledgeArticleIngestionService:
    embedding_model = (
        create_embedding_model()
    )

    client = create_qdrant_client()

    vector_store = create_vector_store(
        client=client,
        embedding_model=embedding_model,
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

def create_gap_verification_service(
) -> KnowledgeGapVerificationService:
    retriever = (
        create_parent_child_retriever()
    )

    semantic_store = (
        create_semantic_knowledge_gap_store()
    )

    return KnowledgeGapVerificationService(
        session_factory=SessionFactory,
        retriever=retriever,
        semantic_store=semantic_store,
        minimum_coverage=(
            settings
            .knowledge_gap_minimum_coverage
        ),
    )

