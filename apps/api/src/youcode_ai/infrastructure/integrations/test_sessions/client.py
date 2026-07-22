from datetime import date

import httpx
from pydantic import ValidationError

from youcode_ai.domain.exceptions import (
    ExternalServiceError,
    TestSessionNotFoundError,
)
from youcode_ai.infrastructure.integrations.test_sessions.schemas import (
    TestSessionData,
    TestSessionListData,
    TestSessionStatus,
    TestType,
)


class TestSessionApiClient:
    def __init__(
        self,
        *,
        base_url: str,
        timeout: float,
    ) -> None:
        self.base_url = (
            base_url.rstrip("/")
        )

        self.timeout = timeout

    def list_sessions(
        self,
        *,
        campus: str,
        date_from: date,
        date_to: date | None = None,
        test_type: TestType = (
            TestType.IN_PERSON
        ),
        status: TestSessionStatus = (
            TestSessionStatus.OPEN
        ),
        minimum_capacity: int = 1,
    ) -> TestSessionListData:
        params: dict[str, str | int] = {
            "campus": campus,
            "date_from": (
                date_from.isoformat()
            ),
            "test_type": test_type.value,
            "status": status.value,
            "minimum_capacity": (
                minimum_capacity
            ),
        }

        if date_to is not None:
            params["date_to"] = (
                date_to.isoformat()
            )

        try:
            response = httpx.get(
                (
                    f"{self.base_url}"
                    "/test-sessions"
                ),
                params=params,
                timeout=self.timeout,
            )

            response.raise_for_status()

            return (
                TestSessionListData
                .model_validate(
                    response.json()
                )
            )
        except (
            httpx.HTTPError,
            ValidationError,
            ValueError,
        ) as error:
            raise ExternalServiceError(
                "Unable to retrieve test "
                "sessions."
            ) from error

    def get_session(
        self,
        session_id: str,
    ) -> TestSessionData:
        try:
            response = httpx.get(
                (
                    f"{self.base_url}"
                    f"/test-sessions/{session_id}"
                ),
                timeout=self.timeout,
            )

            if response.status_code == 404:
                raise (
                    TestSessionNotFoundError(
                        "Test session not found."
                    )
                )

            response.raise_for_status()

            return (
                TestSessionData
                .model_validate(
                    response.json()
                )
            )
        except TestSessionNotFoundError:
            raise
        except (
            httpx.HTTPError,
            ValidationError,
            ValueError,
        ) as error:
            raise ExternalServiceError(
                "Unable to retrieve the "
                "test session."
            ) from error