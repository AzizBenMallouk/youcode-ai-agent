from datetime import date
from typing import Annotated

from fastapi import (
    FastAPI,
    HTTPException,
    Query,
)

from fake_test_session_api.data import (
    TEST_SESSIONS,
)
from fake_test_session_api.schemas import (
    TestSession,
    TestSessionListResponse,
    TestSessionStatus,
    TestType,
)


app = FastAPI(
    title="Fake YouCode Test Session API",
    version="0.1.0",
)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {
        "status": "healthy",
        "service": "test-session-api",
    }


@app.get(
    "/test-sessions",
    response_model=(
        TestSessionListResponse
    ),
)
def list_test_sessions(
    campus: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    test_type: TestType | None = None,
    status: TestSessionStatus | None = None,
    minimum_capacity: Annotated[
        int,
        Query(ge=0),
    ] = 1,
) -> TestSessionListResponse:
    sessions = TEST_SESSIONS

    if campus:
        normalized_campus = (
            campus.strip().lower()
        )

        sessions = [
            session
            for session in sessions
            if session.campus.lower()
            == normalized_campus
        ]

    if date_from:
        sessions = [
            session
            for session in sessions
            if session.start_at.date()
            >= date_from
        ]

    if date_to:
        sessions = [
            session
            for session in sessions
            if session.start_at.date()
            <= date_to
        ]

    if test_type:
        sessions = [
            session
            for session in sessions
            if session.test_type
            == test_type
        ]

    if status:
        sessions = [
            session
            for session in sessions
            if session.status == status
        ]

    sessions = [
        session
        for session in sessions
        if session.available_capacity
        >= minimum_capacity
    ]

    sessions = sorted(
        sessions,
        key=lambda session: (
            session.start_at
        ),
    )

    return TestSessionListResponse(
        items=sessions,
        total=len(sessions),
    )


@app.get(
    "/test-sessions/{session_id}",
    response_model=TestSession,
)
def get_test_session(
    session_id: str,
) -> TestSession:
    for session in TEST_SESSIONS:
        if session.id == session_id:
            return session

    raise HTTPException(
        status_code=404,
        detail="Test session not found.",
    )