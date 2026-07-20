import argparse
import json
from dataclasses import asdict

from youcode_guide.metier.services.knowledge_gap_verification_service import (
    create_gap_verification_service,
)


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "article_id",
        type=int,
    )

    arguments = parser.parse_args()

    service = (
        create_gap_verification_service()
    )

    result = service.verify_article(
        arguments.article_id,
    )

    print(
        json.dumps(
            asdict(result),
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()