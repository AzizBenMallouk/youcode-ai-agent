import hashlib

from pathlib import Path

from langchain_core.documents import (
    Document,
)

from youcode_ai.core.config import (
    PROJECT_ROOT,
    settings,
)


def resolve_documents_path() -> Path:
    documents_path = (
        settings.documents_path
    )

    if documents_path.is_absolute():
        return documents_path

    return (
        PROJECT_ROOT
        / documents_path
    ).resolve()


def generate_document_id(
    *,
    relative_path: str,
    content: str,
) -> str:
    """
    L'identifiant change lorsque le contenu
    du document change.
    """

    value = (
        f"{relative_path}:{content}"
    )

    return hashlib.sha256(
        value.encode("utf-8")
    ).hexdigest()


def extract_title(
    *,
    content: str,
    fallback: str,
) -> str:
    """
    Utilise le premier titre Markdown trouvé.
    """

    for line in content.splitlines():
        normalized_line = line.strip()

        if normalized_line.startswith(
            "#"
        ):
            title = normalized_line.lstrip(
                "#"
            ).strip()

            if title:
                return title

    return fallback


def load_text_documents(
    directory: str | Path | None = None,
) -> list[Document]:
    root_directory = (
        Path(directory)
        if directory is not None
        else resolve_documents_path()
    )

    if not root_directory.exists():
        raise FileNotFoundError(
            "Documents directory not found: "
            f"{root_directory}"
        )

    documents: list[Document] = []

    for file_path in sorted(
        root_directory.rglob("*.txt")
    ):
        if not file_path.is_file():
            continue

        content = file_path.read_text(
            encoding="utf-8"
        ).strip()

        if not content:
            continue

        relative_path = (
            file_path.relative_to(
                root_directory
            )
        )

        relative_path_value = (
            relative_path.as_posix()
        )

        category = (
            relative_path.parts[0]
            if len(relative_path.parts) > 1
            else "general"
        )

        document_id = generate_document_id(
            relative_path=(
                relative_path_value
            ),
            content=content,
        )

        title = extract_title(
            content=content,
            fallback=file_path.stem.replace(
                "_",
                " ",
            ).title(),
        )

        documents.append(
            Document(
                page_content=content,
                metadata={
                    "document_id": (
                        document_id
                    ),
                    "source": (
                        relative_path_value
                    ),
                    "file_name": (
                        file_path.name
                    ),
                    "file_type": "text",
                    "category": category,
                    "title": title,
                },
            )
        )

    return documents