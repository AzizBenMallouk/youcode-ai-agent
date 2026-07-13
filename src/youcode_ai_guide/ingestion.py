from uuid import NAMESPACE_URL, uuid5

from langchain_core.documents import Document

from youcode_ai_guide.config import get_settings
from youcode_ai_guide.embeddings import create_embeddings
from youcode_ai_guide.loaders import load_documents
from youcode_ai_guide.splitter import split_documents
from youcode_ai_guide.vector_store import (
    create_collection,
    create_qdrant_client,
    create_vector_store,
)


def generate_document_id(
    document: Document,
) -> str:
    source = document.metadata.get(
        "source",
        "unknown",
    )

    start_index = document.metadata.get(
        "start_index",
        0,
    )

    unique_value = (
        f"{source}:{start_index}:"
        f"{document.page_content}"
    )

    return str(
        uuid5(
            NAMESPACE_URL,
            unique_value,
        )
    )


def ingest_documents(
    recreate_collection: bool = True,
) -> int:
    settings = get_settings()

    # 1. Charger les documents
    documents = load_documents( # TODO
        settings.documents_path
    )

    if not documents:
        print("Aucun document trouvé.")
        return 0

    # 2. Découper les documents
    chunks = split_documents( # TODO
        documents=documents,
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
    )

    if not chunks:
        print("Aucun chunk généré.")
        return 0

    # 3. Créer le modèle d'embedding
    embeddings = create_embeddings(settings)

    # 4. Déterminer la dimension des vecteurs
    sample_vector = embeddings.embed_query(
        "YouCode"
    )

    vector_size = len(sample_vector)

    print(
        f"Dimension des embeddings : {vector_size}"
    )

    # 5. Se connecter à Qdrant
    client = create_qdrant_client(settings)

    # 6. Créer ou recréer la collection
    create_collection(
        client=client,
        collection_name=settings.qdrant_collection,
        vector_size=vector_size,
        recreate=recreate_collection,
    )

    # 7. Créer le vector store LangChain
    vector_store = create_vector_store( # TODO
        client=client,
        settings=settings,
        embeddings=embeddings,
    )

    # 8. Générer des identifiants stables
    ids = [
        generate_document_id(chunk) # TODO
        for chunk in chunks
    ]

    # 9. Stocker les chunks dans Qdrant
    vector_store.add_documents( # TODO
        documents=chunks,
        ids=ids,
    )

    print(
        f"{len(chunks)} chunk(s) indexé(s) "
        f"dans Qdrant."
    )

    return len(chunks)


def main() -> None:
    ingest_documents(
        recreate_collection=True
    )


if __name__ == "__main__":
    main()