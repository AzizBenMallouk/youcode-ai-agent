from langchain_google_genai import (
    GoogleGenerativeAIEmbeddings,
)

from youcode_guide.config import settings


def create_embedding_model(
) -> GoogleGenerativeAIEmbeddings:
    return GoogleGenerativeAIEmbeddings(
        model=settings.gemini_embedding_model,
        google_api_key=settings.google_api_key,
    )