from youcode_guide.metier.ingestion.ingestion import (
    IngestionService,
)


def main() -> None:
    print("Starting document ingestion...")

    service = IngestionService()

    result = service.run()

    print()
    print("Ingestion completed.")
    print(
        f"Source documents: "
        f"{result['source_documents']}"
    )
    print(
        f"Parent chunks: "
        f"{result['parent_chunks']}"
    )
    print(
        f"Child chunks: "
        f"{result['child_chunks']}"
    )
    print(
        f"Vector dimension: "
        f"{result['vector_size']}"
    )
    print(
        f"Qdrant collection: "
        f"{result['collection']}"
    )


if __name__ == "__main__":
    main()