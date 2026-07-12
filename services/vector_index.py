import json
from pathlib import Path
from typing import Any

from services.embedding_service import (
    EMBEDDING_MODEL,
    create_embedding,
    create_embeddings,
)
from utils.similarity import cosine_similarity


class VectorIndex:
    def __init__(
        self,
        index_path: str = "data/vector_index.json",
    ) -> None:
        self.items: list[dict[str, Any]] = []
        self.index_path = Path(index_path)

    def build(
        self,
        documents: list[dict[str, Any]],
    ) -> None:
        if not documents:
            raise ValueError(
                "La liste des documents est vide."
            )

        texts = [
            document["content"]
            for document in documents
        ]

        embeddings = create_embeddings(texts)

        self.items = [
            {
                "document": document,
                "embedding": embedding,
            }
            for document, embedding in zip(
                documents,
                embeddings,
            )
        ]

    def save(self) -> None:
        if not self.items:
            raise ValueError(
                "Impossible de sauvegarder un index vide."
            )

        self.index_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        data = {
            "model": EMBEDDING_MODEL,
            "items": self.items,
        }

        with self.index_path.open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                data,
                file,
                ensure_ascii=False,
            )

    def load(self) -> None:
        if not self.index_path.exists():
            raise FileNotFoundError(
                f"Index introuvable : {self.index_path}"
            )

        with self.index_path.open(
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)

        saved_model = data.get("model")

        if saved_model != EMBEDDING_MODEL:
            raise ValueError(
                "L'index a été créé avec un autre modèle "
                f"d'embedding : {saved_model}"
            )

        self.items = data.get("items", [])

        if not self.items:
            raise ValueError(
                "Le fichier d'index ne contient aucun document."
            )

    def search(
        self,
        query: str,
        top_k: int = 3,
    ) -> list[dict[str, Any]]:
        if not self.items:
            raise ValueError(
                "L'index est vide."
            )

        if not query.strip():
            raise ValueError(
                "La question ne peut pas être vide."
            )

        if top_k <= 0:
            raise ValueError(
                "top_k doit être supérieur à zéro."
            )

        query_embedding = create_embedding(query)

        results = []

        for item in self.items:
            score = cosine_similarity(
                query_embedding,
                item["embedding"],
            )

            results.append({
                "document": item["document"],
                "score": score,
            })

        results.sort(
            key=lambda result: result["score"],
            reverse=True,
        )

        return results[:top_k]