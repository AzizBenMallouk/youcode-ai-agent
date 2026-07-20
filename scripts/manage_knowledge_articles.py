import argparse

from youcode_guide.metier.services.knowledge_article_service import (
    create_knowledge_article_service,
)
from youcode_guide.metier.enums.knowledge_article_status import (
    KnowledgeArticleStatus,
)


def list_articles(
    service,
    status_value: str | None,
) -> None:
    status = (
        KnowledgeArticleStatus(status_value)
        if status_value
        else None
    )

    articles = service.list_articles(
        status=status,
    )

    if not articles:
        print("Aucun article trouvé.")
        return

    print(
        f"{'ID':<6}"
        f"{'STATUT':<14}"
        f"{'VERSION':<10}"
        f"{'CATÉGORIE':<14}"
        "TITRE"
    )

    print("-" * 90)

    for article in articles:
        print(
            f"{article.id:<6}"
            f"{article.status.value:<14}"
            f"{article.version:<10}"
            f"{article.category:<14}"
            f"{article.title}"
        )


def show_article(
    service,
    article_id: int,
) -> None:
    article = service.get_by_id(
        article_id,
    )

    print(f"ID : {article.id}")
    print(f"Titre : {article.title}")
    print(f"Statut : {article.status.value}")
    print(f"Version : {article.version}")
    print(f"Catégorie : {article.category}")
    print(f"Source : {article.source_name}")
    print(f"Créé par : {article.created_by}")
    print(f"Validé par : {article.reviewed_by}")
    print(f"Publié le : {article.published_at}")
    print(f"Indexé le : {article.indexed_at}")
    print("\nContenu :")
    print(article.content)


def main() -> None:
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    list_parser = subparsers.add_parser(
        "list"
    )

    list_parser.add_argument(
        "--status",
        choices=[
            status.value
            for status
            in KnowledgeArticleStatus
        ],
    )

    show_parser = subparsers.add_parser(
        "show"
    )
    show_parser.add_argument(
        "article_id",
        type=int,
    )

    submit_parser = subparsers.add_parser(
        "submit"
    )
    submit_parser.add_argument(
        "article_id",
        type=int,
    )

    publish_parser = subparsers.add_parser(
        "publish"
    )
    publish_parser.add_argument(
        "article_id",
        type=int,
    )
    publish_parser.add_argument(
        "--reviewed-by",
        required=True,
    )

    reject_parser = subparsers.add_parser(
        "reject"
    )
    reject_parser.add_argument(
        "article_id",
        type=int,
    )
    reject_parser.add_argument(
        "--reviewed-by",
        required=True,
    )

    reopen_parser = subparsers.add_parser(
        "reopen"
    )
    reopen_parser.add_argument(
        "article_id",
        type=int,
    )

    archive_parser = subparsers.add_parser(
        "archive"
    )
    archive_parser.add_argument(
        "article_id",
        type=int,
    )

    arguments = parser.parse_args()

    service = (
        create_knowledge_article_service()
    )

    if arguments.command == "list":
        list_articles(
            service,
            arguments.status,
        )

    elif arguments.command == "show":
        show_article(
            service,
            arguments.article_id,
        )

    elif arguments.command == "submit":
        article = service.submit_for_review(
            arguments.article_id,
        )

        print(
            f"Article {article.id} soumis "
            "pour validation."
        )

    elif arguments.command == "publish":
        article = service.publish(
            article_id=arguments.article_id,
            reviewed_by=(
                arguments.reviewed_by
            ),
        )

        print(
            f"Article {article.id} publié."
        )

    elif arguments.command == "reject":
        article = service.reject(
            article_id=arguments.article_id,
            reviewed_by=(
                arguments.reviewed_by
            ),
        )

        print(
            f"Article {article.id} rejeté."
        )

    elif arguments.command == "reopen":
        article = service.reopen(
            arguments.article_id,
        )

        print(
            f"Article {article.id} "
            "rouvert en brouillon."
        )

    elif arguments.command == "archive":
        article = service.archive(
            arguments.article_id,
        )

        print(
            f"Article {article.id} archivé."
        )


if __name__ == "__main__":
    main()