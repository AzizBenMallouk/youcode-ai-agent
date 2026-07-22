import httpx

from youcode_ai.infrastructure.integrations.registration_api.schemas import (
    RegistrationStatusData,
)


class RegistrationApiClient:
    def __init__(
        self,
        *,
        base_url: str,
        timeout: float,
        api_key: str | None = None,
    ) -> None:
        self.base_url = (
            base_url.rstrip("/")
        )

        self.timeout = timeout
        self.api_key = api_key

    def get_status(
        self,
        *,
        program: str = "full_program",
        campus: str | None = None,
    ) -> RegistrationStatusData:
        params = {
            "program": program,
        }

        if campus:
            params["campus"] = campus

        headers: dict[str, str] = {}

        if self.api_key:
            headers["X-API-Key"] = (
                self.api_key
            )

        with httpx.Client(
            base_url=self.base_url,
            timeout=self.timeout,
            headers=headers,
        ) as client:
            response = client.get(
                "/registration/status",
                params=params,
            )

            response.raise_for_status()

            return (
                RegistrationStatusData
                .model_validate(
                    response.json()
                )
            )