import traceback

from youcode_ai.rag.ingestion import (
    DocumentIngestionService,
)


def main() -> None:
    print(
        "Starting document ingestion..."
    )

    service = (
        DocumentIngestionService()
    )

    try:
        result = service.run()
    except Exception:
        print(
            "Document ingestion failed."
        )

        traceback.print_exc()
        raise SystemExit(1)

    print()
    print(
        "Document ingestion completed."
    )

    print(
        "Source documents:",
        result.source_documents,
    )

    print(
        "Parent chunks:",
        result.parent_chunks,
    )

    print(
        "Child chunks:",
        result.child_chunks,
    )

    print(
        "Indexed children:",
        result.indexed_children,
    )

    print(
        "Vector dimension:",
        result.vector_size,
    )

    print(
        "Collection:",
        result.collection_name,
    )

    print(
        "Embedding provider:",
        result.embedding_provider,
    )


if __name__ == "__main__":
    main()