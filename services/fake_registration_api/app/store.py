from datetime import (
    date,
    datetime,
    timezone,
)

from app.schemas import (
    RegistrationPeriod,
)


class RegistrationStore:
    def __init__(self) -> None:
        self._periods: list[dict] = [
            {
                "id": "REG-FULL-2026",
                "program": "full_program",
                "campus": "all",
                "opening_date": date(
                    2026,
                    8,
                    1,
                ),
                "closing_date": date(
                    2026,
                    8,
                    31,
                ),
                "registration_url": (
                    "https://candidature."
                    "youcode.ma/register"
                ),
                "available_places": None,
                "message": (
                    "Les inscriptions à la "
                    "formation complète ouvriront "
                    "prochainement."
                ),
                "updated_at": datetime.now(
                    timezone.utc
                ),
            },
            {
                "id": "REG-BOOTCAMP-SAFI-2026",
                "program": "bootcamp",
                "campus": "Safi",
                "opening_date": date(
                    2026,
                    7,
                    15,
                ),
                "closing_date": date(
                    2026,
                    8,
                    5,
                ),
                "registration_url": (
                    "https://candidature."
                    "youcode.ma/register"
                ),
                "available_places": 20,
                "message": (
                    "Les candidatures au "
                    "bootcamp de Safi sont "
                    "disponibles."
                ),
                "updated_at": datetime.now(
                    timezone.utc
                ),
            },
        ]

    def list_periods(
        self,
        *,
        program: str | None = None,
        campus: str | None = None,
    ) -> list[RegistrationPeriod]:
        periods = [
            self._to_model(item)
            for item in self._periods
            if self._matches(
                item=item,
                program=program,
                campus=campus,
            )
        ]

        return sorted(
            periods,
            key=lambda period: (
                period.opening_date
                or date.max
            ),
        )

    def find_best_period(
        self,
        *,
        program: str,
        campus: str | None = None,
    ) -> RegistrationPeriod | None:
        """
        Priorité :

        1. période actuellement ouverte ;
        2. prochaine période ;
        3. dernière période fermée.
        """

        periods = self.list_periods(
            program=program,
            campus=campus,
        )

        if not periods:
            return None

        open_periods = [
            period
            for period in periods
            if period.status == "open"
        ]

        if open_periods:
            return open_periods[0]

        upcoming_periods = [
            period
            for period in periods
            if period.status == "upcoming"
        ]

        if upcoming_periods:
            return upcoming_periods[0]

        closed_periods = [
            period
            for period in periods
            if period.status == "closed"
        ]

        if closed_periods:
            return max(
                closed_periods,
                key=lambda period: (
                    period.closing_date
                    or date.min
                ),
            )

        return periods[0]

    @staticmethod
    def _matches(
        *,
        item: dict,
        program: str | None,
        campus: str | None,
    ) -> bool:
        if (
            program
            and item["program"] != program
        ):
            return False

        if campus:
            period_campus = item["campus"]

            if period_campus not in {
                campus,
                "all",
            }:
                return False

        return True

    def _to_model(
        self,
        item: dict,
    ) -> RegistrationPeriod:
        return RegistrationPeriod(
            **item,
            status=self._calculate_status(
                opening_date=item[
                    "opening_date"
                ],
                closing_date=item[
                    "closing_date"
                ],
                available_places=item[
                    "available_places"
                ],
            ),
        )

    @staticmethod
    def _calculate_status(
        *,
        opening_date: date | None,
        closing_date: date | None,
        available_places: int | None,
    ) -> str:
        if (
            opening_date is None
            or closing_date is None
        ):
            return "unknown"

        today = date.today()

        if today < opening_date:
            return "upcoming"

        if today > closing_date:
            return "closed"

        if available_places == 0:
            return "closed"

        return "open"


registration_store = RegistrationStore()