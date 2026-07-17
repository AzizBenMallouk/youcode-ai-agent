from langchain_core.documents import Document

from youcode_guide.rag.retriever import (
    RetrievalResult,
)


def format_documents_for_agent(
    result: RetrievalResult,
) -> str:
    documents: list[Document] = result.parents

    if not documents:
        return (
            "INFORMATION_NOT_AVAILABLE\n"
            "Aucun document officiel suffisamment pertinent "
            "n'a été trouvé."
        )

    formatted_documents: list[str] = []

    for index, document in enumerate(
        documents,
        start=1,
    ):
        metadata = document.metadata

        title = metadata.get(
            "title",
            "Document YouCode",
        )

        category = metadata.get(
            "category",
            "general",
        )

        source = metadata.get(
            "source",
            "source inconnue",
        )

        formatted_documents.append(
            "\n".join(
                [
                    f"DOCUMENT {index}",
                    f"Titre : {title}",
                    f"Catégorie : {category}",
                    f"Source : {source}",
                    "Contenu :",
                    document.page_content.strip(),
                ]
            )
        )

    return "\n\n---\n\n".join(
        formatted_documents,
    )