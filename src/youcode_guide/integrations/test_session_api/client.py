from datetime import date

import httpx
from pydantic import ValidationError

from youcode_guide.integrations.test_session_api.exceptions import (
    InvalidTestSessionResponse,
    TestSessionApiUnavailable,
)
from youcode_guide.integrations.test_session_api.schemas import (
    ExternalTestSessionList,
)


class TestSessionApiClient:
    def __init__(
        self,
        *,
        base_url: str,
        api_key: str | None,
        timeout: float,
    ) -> None:
        headers = {
            "Accept": "application/json",
        }

        if api_key:
            headers["Authorization"] = (
                f"Bearer {api_key}"
            )

        self.client = httpx.Client(
            base_url=base_url,
            headers=headers,
            timeout=timeout,
        )

    def get_next_sessions(
        self,
        *,
        campus: str,
        date_from: date,
        date_to: date | None = None,
    ) -> ExternalTestSessionList:
        parameters: dict[str, str] = {
            "campus": campus,
            "date_from": date_from.isoformat(),
            "status": "open",
        }

        if date_to is not None:
            parameters["date_to"] = (
                date_to.isoformat()
            )

        try:
            response = self.client.get(
                "/test-sessions",
                params=parameters,
            )

            response.raise_for_status()

        except (
            httpx.TimeoutException,
            httpx.NetworkError,
        ) as exception:
            raise TestSessionApiUnavailable(
                "Test session API is unavailable."
            ) from exception

        except httpx.HTTPStatusError as exception:
            raise TestSessionApiUnavailable(
                "Test session API returned "
                f"status {exception.response.status_code}."
            ) from exception

        try:
            return (
                ExternalTestSessionList
                .model_validate(
                    response.json()
                )
            )

        except (
            ValueError,
            ValidationError,
        ) as exception:
            raise InvalidTestSessionResponse(
                "Invalid test session API response."
            ) from exception

    def close(self) -> None:
        self.client.close()