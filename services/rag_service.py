from models.guide_respons import GuideResponse
from prompts.rag_prompt import RAG_SYSTEM_PROMPT
from services.ollama_service import ask_ollama
from services.qdrant_service import search_documents


def build_context(
    search_results: list[dict],
) -> str:
    context_parts = []

    for position, result in enumerate(
        search_results,
        start=1,
    ):
        payload = result["payload"]

        source = payload.get("source", "source_inconnue")
        content = payload.get("content", "")

        context_parts.append(
            f"""
Document {position}
Source : {source}
Contenu :
{content}
""".strip()
        )

    return "\n\n".join(context_parts)


def ask_youcode_guide(
    question: str,
) -> GuideResponse:
    search_results = search_documents(
        query=question,
        top_k=3
    )

    context = build_context(search_results)

    user_prompt = f"""
Contexte documentaire :
<context>
{context}
</context>

Question du visiteur :
<question>
{question}
</question>

Réponds uniquement à partir du contexte documentaire.
"""

    messages = [
        {
            "role": "system",
            "content": RAG_SYSTEM_PROMPT,
        },
        {
            "role": "user",
            "content": user_prompt,
        },
    ]

    raw_answer = ask_ollama(
        messages=messages,
        output_schema=GuideResponse.model_json_schema(),
    )

    return GuideResponse.model_validate_json(raw_answer)