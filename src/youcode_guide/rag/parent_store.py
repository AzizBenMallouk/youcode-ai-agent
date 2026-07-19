import json
from pathlib import Path
from typing import Any

from langchain_core.documents import Document


class ParentDocumentStore:
    def __init__(
        self,
        file_path: str | Path,
    ) -> None:
        self.file_path = Path(file_path)

        self.file_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

    def replace_all(
        self,
        documents: list[Document],
    ) -> str:
        data: dict[str, dict[str, Any]] = {}

        for document in documents:
            parent_id = document.metadata.get(
                "parent_id"
            )

            if not parent_id:
                raise ValueError(
                    "Parent document has no parent_id."
                )

            data[parent_id] = {
                "page_content": document.page_content,
                "metadata": document.metadata,
            }

        return self._write_data(data)

    def load_data(
        self,
    ) -> dict[str, dict[str, Any]]:
        if not self.file_path.exists():
            return {}

        content = self.file_path.read_text(
            encoding="utf-8"
        )

        if not content.strip():
            return {}

        return json.loads(content)

    def get(
        self,
        parent_id: str,
    ) -> Document | None:
        data = self.load_data()

        stored_document = data.get(parent_id)

        if stored_document is None:
            return None

        return Document(
            page_content=stored_document[
                "page_content"
            ],
            metadata=stored_document["metadata"],
        )

    def get_many(
        self,
        parent_ids: list[str],
    ) -> list[Document]:
        data = self.load_data()

        documents: list[Document] = []
        used_ids: set[str] = set()

        for parent_id in parent_ids:
            if parent_id in used_ids:
                continue

            stored_document = data.get(parent_id)

            if stored_document is None:
                continue

            documents.append(
                Document(
                    page_content=stored_document[
                        "page_content"
                    ],
                    metadata=stored_document[
                        "metadata"
                    ],
                )
            )

            used_ids.add(parent_id)

        return documents

    def count(self) -> int:
        return len(self.load_data())
    

    def replace_document(
        self,
        *,
        document_id: str,
        documents: list[Document],
    ) -> str:
        data = self.load_data()

        # Supprimer les anciennes versions des parents
        # de ce document uniquement.
        data = {
            parent_id: stored_document
            for parent_id, stored_document
            in data.items()
            if (
                stored_document
                .get("metadata", {})
                .get("document_id")
                != document_id
            )
        }

        for document in documents:
            parent_id = document.metadata.get(
                "parent_id"
            )

            if not parent_id:
                raise ValueError(
                    "Parent document has no parent_id."
                )

            current_document_id = (
                document.metadata.get(
                    "document_id"
                )
            )

            if current_document_id != document_id:
                raise ValueError(
                    "Parent document has an "
                    "unexpected document_id."
                )

            data[parent_id] = {
                "page_content": (
                    document.page_content
                ),
                "metadata": document.metadata,
            }

        return self._write_data(data)


    def delete_document(
        self,
        document_id: str,
    ) -> None:
        data = self.load_data()

        filtered_data = {
            parent_id: stored_document
            for parent_id, stored_document
            in data.items()
            if (
                stored_document
                .get("metadata", {})
                .get("document_id")
                != document_id
            )
        }

        self._write_data(filtered_data)


    def _write_data(
        self,
        data: dict[str, dict[str, Any]],
    ) -> str:
        temporary_path = self.file_path.with_suffix(
            ".tmp"
        )

        temporary_path.write_text(
            json.dumps(
                data,
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

        return temporary_path.replace(self.file_path)