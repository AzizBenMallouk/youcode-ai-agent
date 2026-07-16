from datetime import datetime, timezone

from youcode_guide.database.connection import (
    create_database_session,
)
from youcode_guide.registration.models import (
    RegistrationState,
    RegistrationStatus,
    UpdateRegistrationStatus,
)
from youcode_guide.registration.repository import (
    RegistrationRepository,
)


class RegistrationService:
    def __init__(
        self,
        repository: RegistrationRepository,
    ) -> None:
        self.repository = repository

    def get_current_status(
        self,
    ) -> RegistrationStatus:
        row = self.repository.get_current()

        if row is None:
            return RegistrationStatus(
                status=RegistrationState.UNKNOWN,
                registration_url=None,
                opening_date=None,
                closing_date=None,
                message=(
                    "Le statut des inscriptions "
                    "n'est pas disponible."
                ),
                updated_at=datetime.now(
                    timezone.utc
                ),
            )

        return RegistrationStatus(
            status=RegistrationState(
                row.status
            ),
            registration_url=(
                row.registration_url
            ),
            opening_date=row.opening_date,
            closing_date=row.closing_date,
            message=row.message,
            updated_at=row.updated_at,
        )

    def update_status(
        self,
        request: UpdateRegistrationStatus,
    ) -> RegistrationStatus:
        self._validate_update(request)

        updated_at = datetime.now(
            timezone.utc
        )

        row = self.repository.save(
            status=request.status.value,
            registration_url=(
                str(request.registration_url)
                if request.registration_url
                else None
            ),
            opening_date=request.opening_date,
            closing_date=request.closing_date,
            message=request.message,
            updated_at=updated_at,
        )

        return RegistrationStatus(
            status=RegistrationState(
                row.status
            ),
            registration_url=(
                row.registration_url
            ),
            opening_date=row.opening_date,
            closing_date=row.closing_date,
            message=row.message,
            updated_at=row.updated_at,
        )

    def _validate_update(
        self,
        request: UpdateRegistrationStatus,
    ) -> None:
        if (
            request.status
            == RegistrationState.OPEN
            and request.registration_url is None
        ):
            raise ValueError(
                "registration_url is required "
                "when registrations are open."
            )

        if (
            request.status
            == RegistrationState.SCHEDULED
            and request.opening_date is None
        ):
            raise ValueError(
                "opening_date is required "
                "when registrations are scheduled."
            )

        if (
            request.opening_date is not None
            and request.closing_date is not None
            and request.closing_date
            <= request.opening_date
        ):
            raise ValueError(
                "closing_date must be after "
                "opening_date."
            )


def create_registration_service(
) -> RegistrationService:
    repository = RegistrationRepository(
        session_factory=(
            create_database_session
        )
    )

    return RegistrationService(repository)