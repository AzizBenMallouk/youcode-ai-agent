import argparse

from youcode_guide.knowledge.factory import (
    create_knowledge_gap_admin_service,
)
from youcode_guide.knowledge.models import (
    KnowledgeGapStatus,
)


def list_gaps(
    service,
    status_value: str | None,
) -> None:
    status = None

    if status_value is not None:
        status = KnowledgeGapStatus(
            status_value,
        )

    gaps = service.list_gaps(
        status=status,
    )

    if not gaps:
        print("Aucun knowledge gap trouvé.")
        return

    print(
        f"{'ID':<6}"
        f"{'STATUT':<14}"
        f"{'NB':<6}"
        f"{'CATÉGORIE':<14}"
        "QUESTION"
    )

    print("-" * 90)

    for gap in gaps:
        print(
            f"{gap.id:<6}"
            f"{gap.status.value:<14}"
            f"{gap.occurrence_count:<6}"
            f"{gap.category:<14}"
            f"{gap.canonical_question}"
        )


def show_gap(
    service,
    gap_id: int,
) -> None:
    details = service.get_details(
        gap_id,
    )

    gap = details.gap

    print(f"ID : {gap.id}")
    print(f"Statut : {gap.status.value}")
    print(f"Catégorie : {gap.category}")
    print(f"Langue : {gap.language}")
    print(
        "Occurrences : "
        f"{gap.occurrence_count}"
    )
    print(
        "Question canonique : "
        f"{gap.canonical_question}"
    )
    print(
        "Vector point ID : "
        f"{gap.vector_point_id}"
    )
    print("\nVariantes :")

    for question in details.questions:
        score = (
            f"{question.semantic_score:.4f}"
            if question.semantic_score
            is not None
            else "-"
        )

        print(
            f"- [{question.language}] "
            f"{question.original_question} "
            f"(score={score})"
        )


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Manage YouCode knowledge gaps."
        )
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    list_parser = subparsers.add_parser(
        "list",
    )

    list_parser.add_argument(
        "--status",
        choices=[
            status.value
            for status in KnowledgeGapStatus
        ],
    )

    show_parser = subparsers.add_parser(
        "show",
    )
    show_parser.add_argument(
        "gap_id",
        type=int,
    )

    review_parser = subparsers.add_parser(
        "review",
    )
    review_parser.add_argument(
        "gap_id",
        type=int,
    )

    reject_parser = subparsers.add_parser(
        "reject",
    )
    reject_parser.add_argument(
        "gap_id",
        type=int,
    )

    reopen_parser = subparsers.add_parser(
        "reopen",
    )
    reopen_parser.add_argument(
        "gap_id",
        type=int,
    )

    arguments = parser.parse_args()

    service = (
        create_knowledge_gap_admin_service()
    )

    if arguments.command == "list":
        list_gaps(
            service,
            arguments.status,
        )

    elif arguments.command == "show":
        show_gap(
            service,
            arguments.gap_id,
        )

    elif arguments.command == "review":
        gap = service.start_review(
            arguments.gap_id,
        )

        print(
            f"Gap {gap.id} mis en révision."
        )

    elif arguments.command == "reject":
        gap = service.reject(
            arguments.gap_id,
        )

        print(
            f"Gap {gap.id} rejeté."
        )

    elif arguments.command == "reopen":
        gap = service.reopen(
            arguments.gap_id,
        )

        print(
            f"Gap {gap.id} rouvert."
        )


if __name__ == "__main__":
    main()