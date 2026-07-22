from youcode_ai.core.config import settings
from sqlalchemy.orm import Session

from youcode_ai.application.services.consent import (
    ConsentService,
)
from youcode_ai.application.services.support_request import (
    SupportRequestService,
)
from youcode_ai.infrastructure.database.repositories import (
    ConsentRepository,
    VisitorRequestRepository,
)
from youcode_ai.application.services.test_session import (
    TestSessionService,
)
from youcode_ai.infrastructure.integrations.test_sessions import (
    TestSessionApiClient,
)
from youcode_ai.application.services.rescheduling import (
    ReschedulingService,
)

def create_consent_service(
    *,
    session: Session,
) -> ConsentService:
    return ConsentService(
        repository=ConsentRepository(
            session=session
        )
    )


def create_support_request_service(
    *,
    session: Session,
) -> SupportRequestService:
    consent_service = (
        create_consent_service(
            session=session
        )
    )

    repository = (
        VisitorRequestRepository(
            session=session
        )
    )

    return SupportRequestService(
        repository=repository,
        consent_service=consent_service,
    )

def create_test_session_service(
) -> TestSessionService:
    client = TestSessionApiClient(
        base_url=(
            settings.test_session_api_url
        ),
        timeout=(
            settings.external_api_timeout
        ),
    )

    return TestSessionService(
        client=client
    )




def create_rescheduling_service(
    *,
    session: Session,
) -> ReschedulingService:
    repository = (
        VisitorRequestRepository(
            session=session
        )
    )

    test_session_service = (
        create_test_session_service()
    )

    return ReschedulingService(
        repository=repository,
        test_session_service=(
            test_session_service
        ),
    )