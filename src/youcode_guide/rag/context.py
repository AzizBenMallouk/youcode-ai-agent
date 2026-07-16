from langchain_core.documents import Document

from youcode_guide.models import (
    SourceReference,
)


NO_CONTEXT_MESSAGE = (
    "Aucune information pertinente n'a été trouvée "
    "dans les documents officiels."
)


def format_context(
    documents: list[Document],
    max_characters: int = 12000,
) -> str:
    if not documents:
        return NO_CONTEXT_MESSAGE

    formatted_documents: list[str] = []
    current_size = 0

    for index, document in enumerate(
        documents,
        start=1,
    ):
        metadata = document.metadata

        source = metadata.get(
            "source",
            "unknown",
        )

        category = metadata.get(
            "category",
            "unknown",
        )

        campus = metadata.get(
            "campus",
        )

        score = metadata.get(
            "relevance_score",
            0.0,
        )

        header_lines = [
            f"[DOCUMENT {index}]",
            f"Source: {source}",
            f"Category: {category}",
        ]

        if campus:
            header_lines.append(
                f"Campus: {campus}"
            )

        header_lines.append(
            f"Relevance score: {score:.4f}"
        )

        formatted_document = (
            "\n".join(header_lines)
            + "\n\n"
            + document.page_content
        )

        new_size = (
            current_size
            + len(formatted_document)
        )

        if new_size > max_characters:
            break

        formatted_documents.append(
            formatted_document
        )

        current_size = new_size

    if not formatted_documents:
        return NO_CONTEXT_MESSAGE

    return "\n\n---\n\n".join(
        formatted_documents
    )


def build_source_references(
    documents: list[Document],
) -> list[SourceReference]:
    sources_by_path: dict[
        str,
        SourceReference,
    ] = {}

    for document in documents:
        metadata = document.metadata

        source_path = metadata.get("source")

        if not source_path:
            continue

        score = metadata.get(
            "relevance_score"
        )

        existing_source = sources_by_path.get(
            source_path
        )

        if (
            existing_source is not None
            and existing_source.relevance_score
            is not None
            and score is not None
            and existing_source.relevance_score
            >= score
        ):
            continue

        sources_by_path[source_path] = (
            SourceReference(
                source=source_path,
                category=metadata.get(
                    "category"
                ),
                campus=metadata.get("campus"),
                relevance_score=score,
            )
        )

    return list(sources_by_path.values())



