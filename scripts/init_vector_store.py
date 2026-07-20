from youcode_guide.config import settings
from youcode_guide.database.vector.vector_store import (
    create_qdrant_client,
    ensure_vector_collections,
)


def main() -> None:
    client = create_qdrant_client()

    ensure_vector_collections(
        client=client,
        vector_size=(
            settings.embedding_dimension
        ),
    )

    print(
        "Collections Qdrant initialisées."
    )


if __name__ == "__main__":
    main()