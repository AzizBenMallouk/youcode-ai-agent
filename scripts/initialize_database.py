from datetime import datetime, timezone

from youcode_guide.database.connection import (
    Base,
    engine,
)
from youcode_guide.database.schema import (
    ConsentGrantTable,
    RegistrationSettingsTable,
    VisitorRequestTable,
)
from youcode_guide.registration.models import (
    RegistrationState,
    UpdateRegistrationStatus,
)
from youcode_guide.registration.service import (
    create_registration_service,
)


def main() -> None:
    # L'import de RegistrationSettingsTable
    # garantit que SQLAlchemy connaît la table.
    _ = ConsentGrantTable
    _ = RegistrationSettingsTable
    _ = VisitorRequestTable

    Base.metadata.create_all(engine)

    service = create_registration_service()

    current = service.get_current_status()

    if current.status == RegistrationState.UNKNOWN:
        service.update_status(
            UpdateRegistrationStatus(
                status=RegistrationState.UNKNOWN,
                message=(
                    "Le statut des inscriptions "
                    "n'a pas encore été configuré."
                ),
            )
        )

    print("Database initialized.")
    print(
        f"Date: "
        f"{datetime.now(timezone.utc).isoformat()}"
    )


if __name__ == "__main__":
    main()