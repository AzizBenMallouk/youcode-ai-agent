import re
import logging
from better_profanity import profanity

from qdrant_client.models import Distance, VectorParams
from langchain_qdrant import QdrantVectorStore
from youcode_ai.core.config import settings
from youcode_ai.core.llm import create_embedding_model
from youcode_ai.infrastructure.vector import get_qdrant_client
from youcode_ai.agents.guardrails.schemas import GuardrailResult

logger = logging.getLogger(__name__)

# Banned patterns for Prompt Injections and system manipulation
INJECTION_PATTERNS = [
    r"(?i)ignore\s+(all\s+)?previous\s+instructions",
    r"(?i)forget\s+everything",
    r"(?i)you\s+are\s+now",
    r"(?i)system\s+prompt",
    r"(?i)developer\s+mode",
    r"(?i)oublie\s+toutes\s+les\s+instructions",
    r"(?i)ignore\s+tes\s+directives"
]

class GuardrailAgentService:
    def __init__(self):
        self.embeddings = create_embedding_model()
        self.qdrant_client = get_qdrant_client()
        self.collection_name = settings.qdrant_guardrails_collection

        # Validate collection exists
        if not self.qdrant_client.collection_exists(self.collection_name):
            logger.warning(f"Guardrails collection '{self.collection_name}' not found. Vector guardrail will be skipped.")
            self.vector_store = None
        else:
            self.vector_store = QdrantVectorStore(
                client=self.qdrant_client,
                collection_name=self.collection_name,
                embedding=self.embeddings,
            )

    def invoke(self, message: str) -> GuardrailResult:
        logger.info(f"Guardrail check started for message length: {len(message)}")

        # LAYER 1: Rule-based Heuristics
        # 1. Length check
        if len(message) > 1000:
            logger.info("Guardrail block: Message too long.")
            return GuardrailResult(is_safe=False, reason="Votre message est trop long. Veuillez être plus concis.")
            
        # 2. Profanity check (English mostly, but catches standard banned words)
        if profanity.contains_profanity(message):
            logger.info("Guardrail block: Profanity detected.")
            return GuardrailResult(is_safe=False, reason="Langage inapproprié détecté. Veuillez rester poli.")

        # 3. Regex Injection check
        for pattern in INJECTION_PATTERNS:
            if re.search(pattern, message):
                logger.info(f"Guardrail block: Prompt injection pattern matched: {pattern}")
                return GuardrailResult(is_safe=False, reason="Tentative de manipulation détectée.")

        # LAYER 2: Semantic Similarity (Embedding check)
        if self.vector_store:
            try:
                # Perform a similarity search with score
                results = self.vector_store.similarity_search_with_score(message, k=1)
                if results:
                    best_match, score = results[0]
                    # score interpretation for COSINE depends on the Langchain Qdrant integration.
                    # QdrantVectorStore uses similarity (higher is better for cosine).
                    # A threshold of 0.80 means very high semantic similarity.
                    if score > 0.80:
                        logger.info(f"Guardrail block: Semantic similarity too high ({score:.2f}) with: {best_match.page_content}")
                        return GuardrailResult(is_safe=False, reason="Contenu malveillant détecté (Similarité Sémantique).")
            except Exception as e:
                logger.exception("Error querying Qdrant guardrail collection. Skipping semantic check.")

        logger.info("Guardrail check passed. Message is safe.")
        return GuardrailResult(is_safe=True, reason="")

def create_guardrail_agent_service() -> GuardrailAgentService:
    return GuardrailAgentService()
