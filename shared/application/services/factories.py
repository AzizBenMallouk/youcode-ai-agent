from shared.application.services.registration import RegistrationService
from shared.core.config import settings
from shared.infrastructure.integrations.registration_api.client import (
    RegistrationApiClient,
)

def create_registration_service() -> RegistrationService:
    client = RegistrationApiClient(
        base_url=(settings.registration_api_url),
        timeout=(settings.external_api_timeout),
        api_key=(settings.registration_api_key),
    )

    return RegistrationService(client=client)
