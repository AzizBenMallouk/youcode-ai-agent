import json

from json import JSONDecodeError
from pathlib import Path
from typing import Any

from langchain_core.documents import (
    Document,
)

from youcode_ai.core.config import (
    PROJECT_ROOT,
    settings,
)


class ParentDocumentStore:
    def __init__(
        self,
        file_path: str | Path,
    ) -> None:
        self.file_path = Path(
            file_path
        )

        if not self.file_path.is_absolute():
            self.file_path = (
                PROJECT_ROOT
                / self.file_path
            ).resolve()

        self.file_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

    def replace_all(
        self,
        documents: list[Document],
    ) -> None:
        """
        Remplace atomiquement tous les parents.

        Utilisé pendant l'ingestion.
        """

        serialized_documents: dict[
            str,
            dict[str, Any],
        ] = {}

        for document in documents:
            parent_id = (
                document.metadata.get(
                    "parent_id"
                )
            )

            if not parent_id:
                raise ValueError(
                    "Parent document has no "
                    "parent_id."
                )

            if (
                parent_id
                in serialized_documents
            ):
                raise ValueError(
                    "Duplicate parent ID: "
                    f"{parent_id}"
                )

            serialized_documents[
                parent_id
            ] = {
                "page_content": (
                    document.page_content
                ),
                "metadata": (
                    document.metadata
                ),
            }

        temporary_path = (
            self.file_path.with_name(
                self.file_path.name
                + ".tmp"
            )
        )

        temporary_path.write_text(
            json.dumps(
                serialized_documents,
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

        # Remplacement atomique :
        # l'ancien fichier reste valide tant que
        # le nouveau n'est pas complètement écrit.
        temporary_path.replace(
            self.file_path
        )

    def get(
        self,
        parent_id: str,
    ) -> Document | None:
        stored_documents = (
            self._load_data()
        )

        stored_document = (
            stored_documents.get(
                parent_id
            )
        )

        if stored_document is None:
            return None

        return self._deserialize_document(
            stored_document
        )

    def get_many(
        self,
        parent_ids: list[str],
    ) -> list[Document]:
        """
        Récupère les parents en conservant leur
        ordre et en supprimant les doublons.
        """

        stored_documents = (
            self._load_data()
        )

        documents: list[Document] = []
        used_parent_ids: set[str] = set()

        for parent_id in parent_ids:
            if parent_id in used_parent_ids:
                continue

            stored_document = (
                stored_documents.get(
                    parent_id
                )
            )

            if stored_document is None:
                continue

            documents.append(
                self._deserialize_document(
                    stored_document
                )
            )

            used_parent_ids.add(
                parent_id
            )

        return documents

    def count(self) -> int:
        return len(
            self._load_data()
        )

    def exists(self) -> bool:
        return self.file_path.exists()

    def _load_data(
        self,
    ) -> dict[str, dict[str, Any]]:
        if not self.file_path.exists():
            return {}

        content = self.file_path.read_text(
            encoding="utf-8"
        )

        if not content.strip():
            return {}

        try:
            data = json.loads(content)
        except JSONDecodeError as error:
            raise RuntimeError(
                "Parent document store "
                "contains invalid JSON."
            ) from error

        if not isinstance(data, dict):
            raise RuntimeError(
                "Parent document store must "
                "contain a JSON object."
            )

        return data

    @staticmethod
    def _deserialize_document(
        stored_document: dict[str, Any],
    ) -> Document:
        page_content = (
            stored_document.get(
                "page_content"
            )
        )

        metadata = stored_document.get(
            "metadata"
        )

        if not isinstance(
            page_content,
            str,
        ):
            raise RuntimeError(
                "Stored parent document has "
                "invalid page content."
            )

        if not isinstance(
            metadata,
            dict,
        ):
            raise RuntimeError(
                "Stored parent document has "
                "invalid metadata."
            )

        return Document(
            page_content=page_content,
            metadata=metadata,
        )


def create_parent_document_store(
) -> ParentDocumentStore:
    return ParentDocumentStore(
        settings.parent_store_path
    )