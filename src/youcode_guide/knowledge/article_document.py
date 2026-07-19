from langchain_core.documents import Document

from youcode_guide.knowledge.models import (
    KnowledgeArticle,
)


def article_to_document(
    article: KnowledgeArticle,
    *,
    gap_ids: list[int],
) -> Document:
    if article.id is None:
        raise ValueError(
            "Knowledge article has no ID."
        )

    document_id = (
        f"knowledge_article:"
        f"{article.document_key}"
    )

    page_content = (
        f"# {article.title}\n\n"
        f"{article.content}"
    )

    metadata = {
        "document_id": document_id,
        "source": "admin_knowledge_base",
        "source_type": "knowledge_article",
        "article_id": article.id,
        "document_key": article.document_key,
        "title": article.title,
        "category": article.category,
        "version": article.version,
        "status": article.status.value,
        "approved": True,
        "gap_ids": gap_ids,
    }

    if article.source_name:
        metadata["source_name"] = (
            article.source_name
        )

    if article.published_at:
        metadata["published_at"] = (
            article.published_at.isoformat()
        )

    if article.valid_from:
        metadata["valid_from"] = (
            article.valid_from.isoformat()
        )

    if article.valid_until:
        metadata["valid_until"] = (
            article.valid_until.isoformat()
        )

    return Document(
        page_content=page_content,
        metadata=metadata,
    )