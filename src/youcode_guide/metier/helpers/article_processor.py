import hashlib
from youcode_guide.metier.helpers.article_processor import ProcessedKnowledgeArticle


def process_knowledge_article(
    *,
    title: str,
    content: str,
) -> ProcessedKnowledgeArticle:
    cleaned_title = " ".join(
        title.strip().split()
    )

    cleaned_content = "\n".join(
        line.rstrip()
        for line in content.strip().splitlines()
    )

    if not cleaned_title:
        raise ValueError(
            "Article title is required."
        )

    if len(cleaned_title) > 255:
        raise ValueError(
            "Article title is too long."
        )

    if not cleaned_content:
        raise ValueError(
            "Article content is required."
        )

    if len(cleaned_content) < 20:
        raise ValueError(
            "Article content is too short."
        )

    hash_input = (
        f"{cleaned_title}\n{cleaned_content}"
    )

    content_hash = hashlib.sha256(
        hash_input.encode("utf-8"),
    ).hexdigest()

    return ProcessedKnowledgeArticle(
        title=cleaned_title,
        content=cleaned_content,
        content_hash=content_hash,
    )