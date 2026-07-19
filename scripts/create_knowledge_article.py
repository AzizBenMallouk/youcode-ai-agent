import argparse
from pathlib import Path

from youcode_guide.knowledge.factory import (
    create_knowledge_article_service,
)


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--gap-id",
        type=int,
        required=True,
    )

    parser.add_argument(
        "--title",
        required=True,
    )

    parser.add_argument(
        "--category",
        required=True,
        choices=[
            "general",
            "admission",
            "program",
            "campus",
            "pedagogy",
            "career",
            "event",
            "practical",
        ],
    )

    parser.add_argument(
        "--content-file",
        required=True,
    )

    parser.add_argument(
        "--created-by",
        default="cli-admin",
    )

    parser.add_argument(
        "--source-name",
        default=None,
    )

    arguments = parser.parse_args()

    content_path = Path(
        arguments.content_file,
    )

    if not content_path.exists():
        raise FileNotFoundError(
            f"File not found: {content_path}"
        )

    content = content_path.read_text(
        encoding="utf-8",
    )

    service = (
        create_knowledge_article_service()
    )

    article = service.create_draft(
        gap_id=arguments.gap_id,
        title=arguments.title,
        content=content,
        category=arguments.category,
        created_by=arguments.created_by,
        source_name=arguments.source_name,
    )

    print(
        f"Article {article.id} créé "
        f"avec le statut "
        f"{article.status.value}."
    )


if __name__ == "__main__":
    main()