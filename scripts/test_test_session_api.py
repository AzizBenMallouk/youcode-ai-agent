from datetime import date

from youcode_guide.config import settings
from youcode_guide.integrations.test_session_api.client import (
    TestSessionApiClient,
)


def main() -> None:
    print(
        "API URL:",
        settings.test_session_api_url,
    )

    client = TestSessionApiClient(
        base_url=(
            settings.test_session_api_url
        ),
        api_key=(
            settings.test_session_api_key
        ),
        timeout=(
            settings.test_session_api_timeout
        ),
    )

    try:
        response = client.get_next_sessions(
            campus="Safi",
            date_from=date(
                2026,
                8,
                10,
            ),
        )

        print(
            response.model_dump_json(
                indent=2,
            )
        )

    finally:
        client.close()


if __name__ == "__main__":
    main()