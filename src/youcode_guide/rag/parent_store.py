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
    ) -> None:
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

        temporary_path.replace(self.file_path)

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