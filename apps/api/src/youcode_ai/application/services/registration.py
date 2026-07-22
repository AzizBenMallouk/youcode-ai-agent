import logging
from dataclasses import dataclass
from datetime import (
    date,
    datetime,
)
from typing import Literal

import httpx
from pydantic import ValidationError

from youcode_ai.infrastructure.integrations.registration_api.client import (
    RegistrationApiClient,
)


logger = logging.getLogger(__name__)


RegistrationStatus = Literal[
    "open",
    "upcoming",
    "closed",
    "unknown",
    "unavailable",
]


@dataclass(frozen=True)
class RegistrationResult:
    program: str
    campus: str | None

    status: RegistrationStatus

    opening_date: date | None = None
    closing_date: date | None = None

    registration_url: str | None = None
    available_places: int | None = None

    message: str | None = None
    updated_at: datetime | None = None

    service_available: bool = True
    information_available: bool = True


class RegistrationService:
    def __init__(
        self,
        *,
        client: RegistrationApiClient,
    ) -> None:
        self.client = client

    def get_status(
        self,
        *,
        program: str = "full_program",
        campus: str | None = None,
    ) -> RegistrationResult:
        normalized_program = (
            self._normalize_program(
                program
            )
        )

        normalized_campus = (
            self._normalize_campus(
                campus
            )
        )

        try:
            data = self.client.get_status(
                program=normalized_program,
                campus=normalized_campus,
            )

            return RegistrationResult(
                program=data.program,
                campus=data.campus,
                status=data.status,
                opening_date=(
                    data.opening_date
                ),
                closing_date=(
                    data.closing_date
                ),
                registration_url=(
                    data.registration_url
                ),
                available_places=(
                    data.available_places
                ),
                message=data.message,
                updated_at=data.updated_at,
                service_available=True,
                information_available=(
                    data.status != "unknown"
                ),
            )

        except (
            httpx.RequestError,
            httpx.HTTPStatusError,
            ValidationError,
        ):
            logger.exception(
                "Registration API request "
                "failed."
            )

            return RegistrationResult(
                program=normalized_program,
                campus=normalized_campus,
                status="unavailable",
                message=(
                    "Registration service is "
                    "temporarily unavailable."
                ),
                service_available=False,
                information_available=False,
            )

    @staticmethod
    def _normalize_program(
        program: str,
    ) -> str:
        normalized = (
            program.strip().lower()
        )

        aliases = {
            "full_program": "full_program",
            "full program": "full_program",
            "formation": "full_program",
            "formation complète": (
                "full_program"
            ),
            "bootcamp": "bootcamp",
            "bootcamps": "bootcamp",
        }

        result = aliases.get(normalized)

        if result is None:
            raise ValueError(
                f"Unsupported program: "
                f"{program}"
            )

        return result

    @staticmethod
    def _normalize_campus(
        campus: str | None,
    ) -> str | None:
        if campus is None:
            return None

        normalized = (
            campus.strip().lower()
        )

        aliases = {
            "safi": "Safi",
            "youssoufia": "Youssoufia",
            "nador": "Nador",
        }

        result = aliases.get(normalized)

        if result is None:
            raise ValueError(
                f"Unsupported campus: "
                f"{campus}"
            )

        return result
