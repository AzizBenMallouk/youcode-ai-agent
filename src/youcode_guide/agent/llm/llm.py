from langchain_google_genai import (
    ChatGoogleGenerativeAI,
)

from youcode_guide.config import settings


def create_chat_model() -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(
        model=settings.gemini_chat_model,
        google_api_key=settings.google_api_key,
        temperature=0,
        max_retries=2,
        timeout=60,
    )