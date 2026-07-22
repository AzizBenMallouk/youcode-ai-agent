from typing import Literal

from fastapi import (
    FastAPI,
    Query,
)

from app.schemas import (
    RegistrationPeriodList,
    RegistrationStatusResponse,
)
from app.store import (
    registration_store,
)


app = FastAPI(
    title="Fake YouCode Registration API",
    description=(
        "API simulant les informations "
        "dynamiques d'inscription à YouCode."
    ),
    version="0.1.0",
)


Program = Literal[
    "full_program",
    "bootcamp",
]


Campus = Literal[
    "Safi",
    "Youssoufia",
    "Nador",
]


@app.get(
    "/health",
    tags=["Health"],
)
def health_check() -> dict[str, str]:
    return {
        "status": "healthy",
        "service": (
            "fake-registration-api"
        ),
    }


@app.get(
    "/registration/periods",
    response_model=RegistrationPeriodList,
    tags=["Registration"],
)
def list_registration_periods(
    program: Program | None = Query(
        default=None
    ),
    campus: Campus | None = Query(
        default=None
    ),
) -> RegistrationPeriodList:
    periods = (
        registration_store.list_periods(
            program=program,
            campus=campus,
        )
    )

    return RegistrationPeriodList(
        items=periods,
        total=len(periods),
    )


@app.get(
    "/registration/status",
    response_model=(
        RegistrationStatusResponse
    ),
    tags=["Registration"],
)
def get_registration_status(
    program: Program = Query(
        default="full_program"
    ),
    campus: Campus | None = Query(
        default=None
    ),
) -> RegistrationStatusResponse:
    period = (
        registration_store.find_best_period(
            program=program,
            campus=campus,
        )
    )

    if period is None:
        return RegistrationStatusResponse(
            program=program,
            campus=campus,
            status="unknown",
            message=(
                "Aucune période d'inscription "
                "n'est actuellement disponible "
                "pour ces critères."
            ),
        )

    return RegistrationStatusResponse(
        program=period.program,
        campus=(
            campus
            if period.campus == "all"
            else period.campus
        ),
        status=period.status,
        opening_date=(
            period.opening_date
        ),
        closing_date=(
            period.closing_date
        ),
        registration_url=(
            period.registration_url
        ),
        available_places=(
            period.available_places
        ),
        message=period.message,
        updated_at=period.updated_at,
    )