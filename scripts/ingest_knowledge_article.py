import argparse
import json

from youcode_guide.metier.services.article_ingestion_service import (
    create_article_ingestion_service,
)


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "article_id",
        type=int,
    )

    arguments = parser.parse_args()

    service = (
        create_article_ingestion_service()
    )

    result = service.ingest(
        arguments.article_id,
    )

    print(
        json.dumps(
            result,
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()