from datetime import date

from fastapi import (
    FastAPI,
    Query,
)

from fake_test_session_api.data import (
    TEST_SESSIONS,
)
from fake_test_session_api.models import (
    TestSessionListResponse,
    TestSessionResponse,
)


app = FastAPI(
    title="Fake YouCode Test Session API",
    description=(
        "API simulant les prochaines sessions "
        "de test YouCode."
    ),
    version="1.0.0",
)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {
        "status": "healthy",
    }


@app.get(
    "/test-sessions",
    response_model=TestSessionListResponse,
)
def get_test_sessions(
    campus: str,
    date_from: date,
    date_to: date | None = None,
    status: str = "open",
    test_type: str | None = None,
    limit: int = Query(
        default=10,
        ge=1,
        le=100,
    ),
) -> TestSessionListResponse:
    normalized_campus = (
        campus.strip().casefold()
    )

    sessions = [
        session
        for session in TEST_SESSIONS
        if (
            session.campus.casefold()
            == normalized_campus
        )
        and (
            session.scheduled_at.date()
            >= date_from
        )
        and (
            date_to is None
            or session.scheduled_at.date()
            <= date_to
        )
        and session.status == status
        and (
            test_type is None
            or session.test_type
            == test_type
        )
    ]

    sessions.sort(
        key=lambda session: (
            session.scheduled_at
        )
    )

    sessions = sessions[:limit]

    items = [
        TestSessionResponse(
            id=session.id,
            campus=session.campus,
            test_type=session.test_type,
            scheduled_at=(
                session.scheduled_at
            ),
            available_places=(
                session.available_places
            ),
            status=session.status,
        )
        for session in sessions
    ]

    return TestSessionListResponse(
        items=items,
        total=len(items),
    )