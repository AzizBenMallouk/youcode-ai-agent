from qdrant_client import QdrantClient
client = QdrantClient(url="http://localhost:6333")
for c in client.get_collections().collections:
    info = client.get_collection(c.name)
    print(f"{c.name}: {info.config.params.vectors.size}")
