from services.qdrant_service import (
    collection_name,
    client,
    create_collection,
)


create_collection()

collection = client.get_collection(
    collection_name=collection_name,
)

print(collection)