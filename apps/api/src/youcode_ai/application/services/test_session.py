from datetime import date

from youcode_ai.domain.exceptions import (
    NoAvailableTestSessionError,
    TestSessionNotFoundError,
)
from youcode_ai.infrastructure.integrations.test_sessions import (
    TestSessionApiClient,
    TestSessionData,
    TestSessionStatus,
    TestType,
)


class TestSessionService:
    def __init__(
        self,
        *,
        client: TestSessionApiClient,
    ) -> None:
        self.client = client

    def find_available_sessions(
        self,
        *,
        campus: str,
        date_from: date,
        date_to: date | None = None,
    ) -> list[TestSessionData]:
        result = self.client.list_sessions(
            campus=campus,
            date_from=date_from,
            date_to=date_to,
            test_type=TestType.IN_PERSON,
            status=TestSessionStatus.OPEN,
            minimum_capacity=1,
        )

        compatible_sessions = [
            session
            for session in result.items
            if (
                session.campus.lower()
                == campus.strip().lower()
                and session.status
                == TestSessionStatus.OPEN
                and session.available_capacity
                > 0
                and session.start_at.date()
                >= date_from
            )
        ]

        return sorted(
            compatible_sessions,
            key=lambda session: (
                session.start_at
            ),
        )

    def find_best_session(
        self,
        *,
        campus: str,
        requested_date: date,
    ) -> TestSessionData:
        sessions = (
            self.find_available_sessions(
                campus=campus,
                date_from=requested_date,
            )
        )

        if not sessions:
            raise (
                NoAvailableTestSessionError(
                    "No compatible test "
                    "session is available."
                )
            )

        # Le choix est déterministe.
        # Le LLM ne choisit pas la date.
        return sessions[0]

    def validate_session(
        self,
        *,
        session_id: str,
        campus: str,
        requested_date: date,
    ) -> TestSessionData:
        session = self.client.get_session(
            session_id
        )

        if (
            session.status
            != TestSessionStatus.OPEN
        ):
            raise TestSessionNotFoundError(
                "The selected session "
                "is not open."
            )

        if session.available_capacity <= 0:
            raise TestSessionNotFoundError(
                "The selected session "
                "has no available capacity."
            )

        if (
            session.campus.lower()
            != campus.strip().lower()
        ):
            raise TestSessionNotFoundError(
                "The selected session does "
                "not belong to the requested "
                "campus."
            )

        if (
            session.start_at.date()
            < requested_date
        ):
            raise TestSessionNotFoundError(
                "The selected session is "
                "before the requested date."
            )

        return session