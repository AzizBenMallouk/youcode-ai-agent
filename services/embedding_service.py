import os
import requests
from dotenv import load_dotenv

load_dotenv()

llama_url = os.getenv("LLAMA_URL")
llama_model = os.getenv("EMBEDDING_MODEL")


def create_embeddings(texts: list[str]) -> list[list[float]]:
    response = requests.post(
        llama_url+"embed",
        json={
            "model": llama_model,
            "input": texts,
        },
        timeout=120,
    )

    response.raise_for_status()

    data = response.json()

    return data["embeddings"]


def create_embedding(text: str) -> list[float]:
    embeddings = create_embeddings([text])

    return embeddings[0]
