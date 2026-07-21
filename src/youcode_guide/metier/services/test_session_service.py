from datetime import date
from functools import lru_cache

from youcode_guide.config import settings
from youcode_guide.integrations.test_session_api.client import (
    TestSessionApiClient,
)
from youcode_guide.metier.models.test_session import (
    TestSession,
)


class TestSessionService:
    def __init__(
        self,
        api_client: TestSessionApiClient,
    ) -> None:
        self.api_client = api_client

    def find_next_sessions(
        self,
        *,
        campus: str,
        date_from: date,
        date_to: date | None = None,
        limit: int = 5,
    ) -> list[TestSession]:
        response = (
            self.api_client.get_next_sessions(
                campus=campus,
                date_from=date_from,
                date_to=date_to,
            )
        )

        available_sessions = [
            session
            for session in response.items
            if session.status == "open"
            and session.scheduled_at.date()
            >= date_from
            and (
                session.available_places is None
                or session.available_places > 0
            )
        ]

        available_sessions.sort(
            key=lambda session: (
                session.scheduled_at
            )
        )

        return [
            TestSession(
                external_id=session.id,
                campus=session.campus,
                test_type=session.test_type,
                scheduled_at=(
                    session.scheduled_at
                ),
                available_places=(
                    session.available_places
                ),
            )
            for session in available_sessions[
                :limit
            ]
        ]
    



@lru_cache(maxsize=1)
def create_test_session_service(
) -> TestSessionService:
    client = TestSessionApiClient(
        base_url=(
            settings.test_session_api_url
        ),
        api_key=(
            settings.test_session_api_key
        ),
        timeout=(
            settings.test_session_api_timeout
        ),
    )

    return TestSessionService(
        api_client=client,
    )