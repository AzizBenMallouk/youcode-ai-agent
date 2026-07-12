from data.youcode_documents import DOCUMENTS
from services.qdrant_service import (
    collection_name,
    client,
    index_documents,
)


index_documents(DOCUMENTS)

collection = client.get_collection(
    collection_name=collection_name,
)

print(
    "Nombre de points :",
    collection.points_count,
)