import hashlib
from pathlib import Path
from typing import Any

from langchain_core.documents import Document


SUPPORTED_CATEGORIES = {
    "general",
    "admission",
    "program",
    "campus",
    "pedagogy",
    "career",
    "event",
    "practical",
}


def calculate_checksum(content: str) -> str:
    return hashlib.sha256(
        content.encode("utf-8")
    ).hexdigest()


def extract_title(content: str) -> str:
    for line in content.splitlines():
        clean_line = line.strip()

        if clean_line:
            return clean_line.lstrip("#").strip()

    return "Untitled document"


def create_document_id(
    relative_path: Path,
) -> str:
    without_suffix = relative_path.with_suffix("")

    return ":".join(without_suffix.parts)


def build_metadata(
    file_path: Path,
    documents_root: Path,
    content: str,
    language: str,
) -> dict[str, Any]:
    relative_path = file_path.relative_to(
        documents_root
    )

    if len(relative_path.parts) < 2:
        raise ValueError(
            f"The document must be inside a category "
            f"folder: {file_path}"
        )

    category = relative_path.parts[0].lower()

    if category not in SUPPORTED_CATEGORIES:
        raise ValueError(
            f"Unsupported category '{category}' "
            f"for document: {file_path}"
        )

    metadata: dict[str, Any] = {
        "document_id": create_document_id(
            relative_path
        ),
        "source": relative_path.as_posix(),
        "title": extract_title(content),
        "category": category,
        "language": language,
        "file_type": file_path.suffix.lstrip(
            "."
        ).lower(),
        "checksum": calculate_checksum(content),
    }

    if category == "campus":
        metadata["campus"] = (
            file_path.stem.lower()
        )

    return metadata


def load_text_document(
    file_path: Path,
    documents_root: Path,
    language: str = "fr",
) -> Document | None:
    content = file_path.read_text(
        encoding="utf-8"
    ).strip()

    if not content:
        return None

    metadata = build_metadata(
        file_path=file_path,
        documents_root=documents_root,
        content=content,
        language=language,
    )

    return Document(
        page_content=content,
        metadata=metadata,
    )


def load_text_documents(
    documents_path: str | Path,
    language: str = "fr",
) -> list[Document]:
    documents_root = Path(documents_path)

    if not documents_root.exists():
        raise FileNotFoundError(
            f"Documents directory not found: "
            f"{documents_root}"
        )

    if not documents_root.is_dir():
        raise NotADirectoryError(
            f"Documents path is not a directory: "
            f"{documents_root}"
        )

    documents: list[Document] = []

    for file_path in sorted(
        documents_root.rglob("*.txt")
    ):
        document = load_text_document(
            file_path=file_path,
            documents_root=documents_root,
            language=language,
        )

        if document is not None:
            documents.append(document)

    return documents