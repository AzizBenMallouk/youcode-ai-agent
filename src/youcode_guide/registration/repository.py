from collections.abc import Callable
from datetime import datetime

from sqlalchemy.orm import Session

from youcode_guide.database.schema import (
    RegistrationSettingsTable,
)


class RegistrationRepository:
    def __init__(
        self,
        session_factory: Callable[
            [],
            Session,
        ],
    ) -> None:
        self.session_factory = session_factory

    def get_current(
        self,
    ) -> RegistrationSettingsTable | None:
        with self.session_factory() as session:
            return session.get(
                RegistrationSettingsTable,
                1,
            )

    def save(
        self,
        status: str,
        registration_url: str | None,
        opening_date: datetime | None,
        closing_date: datetime | None,
        message: str | None,
        updated_at: datetime,
    ) -> RegistrationSettingsTable:
        with self.session_factory() as session:
            settings_row = session.get(
                RegistrationSettingsTable,
                1,
            )

            if settings_row is None:
                settings_row = (
                    RegistrationSettingsTable(
                        id=1,
                        status=status,
                        registration_url=(
                            registration_url
                        ),
                        opening_date=opening_date,
                        closing_date=closing_date,
                        message=message,
                        updated_at=updated_at,
                    )
                )

                session.add(settings_row)

            else:
                settings_row.status = status

                settings_row.registration_url = (
                    registration_url
                )

                settings_row.opening_date = (
                    opening_date
                )

                settings_row.closing_date = (
                    closing_date
                )

                settings_row.message = message
                settings_row.updated_at = updated_at

            session.commit()
            session.refresh(settings_row)

            return settings_row