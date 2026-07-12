import os
from dotenv import load_dotenv
from typing import Any
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from services.embedding_service import create_embedding, create_embeddings


load_dotenv()

qdrant_url = os.getenv("QDRANT_URL")
collection_name = os.getenv("COLLECTION_NAME")



client = QdrantClient(url=qdrant_url)


def create_collection() -> None:
    if client.collection_exists(collection_name):
        print(
            f"La collection '{collection_name}' existe déjà."
        )
        return

    example_embedding = create_embedding(
        "Texte utilisé pour détecter la dimension."
    )

    vector_size = len(example_embedding)

    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(
            size=vector_size,
            distance=Distance.COSINE,
        ),
    )

    print(
        f"Collection '{collection_name}' créée "
        f"avec {vector_size} dimensions."
    )


def recreate_collection() -> None:
    if client.collection_exists(collection_name):
        client.delete_collection(
            collection_name=collection_name,
        )

    create_collection()



def index_documents(
    documents: list[dict[str, Any]],
) -> None:
    if not documents:
        raise ValueError(
            "Aucun document à indexer."
        )

    create_collection()

    texts = [
        document["content"]
        for document in documents
    ]

    embeddings = create_embeddings(texts)

    points = []

    for document, embedding in zip(
        documents,
        embeddings,
    ):
        point = PointStruct(
            id=document["id"],
            vector=embedding,
            payload={
                "category": document["category"],
                "language": document["language"],
                "source": document["source"],
                "content": document["content"],
            },
        )

        points.append(point)

    client.upsert(
        collection_name=collection_name,
        points=points,
        wait=True,
    )

    print(
        f"{len(points)} documents indexés dans Qdrant."
    )



def search_documents(
    query: str,
    top_k: int = 3,
) -> list[dict[str, Any]]:
    if not query.strip():
        raise ValueError(
            "La question ne peut pas être vide."
        )

    if top_k <= 0:
        raise ValueError(
            "top_k doit être supérieur à zéro."
        )

    if not client.collection_exists(collection_name):
        raise ValueError(
            f"La collection '{collection_name}' n'existe pas."
        )

    query_embedding = create_embedding(query)

    response = client.query_points(
        collection_name=collection_name,
        query=query_embedding,
        limit=top_k,
        with_payload=True,
        with_vectors=False,
    )

    results = []

    for point in response.points:
        results.append({
            "id": point.id,
            "score": point.score,
            "payload": point.payload or {},
        })

    return results



