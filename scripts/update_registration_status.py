import argparse
from datetime import datetime

from youcode_guide.metier.models.update_registration_status import UpdateRegistrationStatus
from youcode_guide.metier.enums.registration_state import RegistrationState
from youcode_guide.metier.services.registration_service import (
    create_registration_service,
)


def parse_datetime(
    value: str | None,
) -> datetime | None:
    if value is None:
        return None

    return datetime.fromisoformat(value)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Update YouCode registration status"
        )
    )

    parser.add_argument(
        "status",
        choices=[
            state.value
            for state in RegistrationState
        ],
    )

    parser.add_argument(
        "--url",
        default=None,
    )

    parser.add_argument(
        "--opening-date",
        default=None,
    )

    parser.add_argument(
        "--closing-date",
        default=None,
    )

    parser.add_argument(
        "--message",
        default=None,
    )

    arguments = parser.parse_args()

    service = create_registration_service()

    result = service.update_status(
        UpdateRegistrationStatus(
            status=RegistrationState(
                arguments.status
            ),
            registration_url=arguments.url,
            opening_date=parse_datetime(
                arguments.opening_date
            ),
            closing_date=parse_datetime(
                arguments.closing_date
            ),
            message=arguments.message,
        )
    )

    print(
        result.model_dump_json(indent=2)
    )


if __name__ == "__main__":
    main()