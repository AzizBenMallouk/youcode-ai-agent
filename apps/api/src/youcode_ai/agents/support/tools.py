import logging

from datetime import date
from typing import Any

from langchain.tools import (
    ToolRuntime,
    tool,
)
from pydantic import ValidationError

from youcode_ai.agents.support.context import (
    SupportAgentContext,
)
from youcode_ai.application.schemas import (
    SupportRequestCreate,
)
from youcode_ai.application.services import (
    create_rescheduling_service,
    create_support_request_service,
)
from youcode_ai.domain.enums import (
    Language,
    RequestType,
)
from youcode_ai.domain.exceptions import (
    DomainError,
)
from youcode_ai.infrastructure.database import (
    database_session,
)


logger = logging.getLogger(__name__)


@tool
def create_support_request(
    request_type: RequestType,
    email: str,
    language: Language,
    description: str,
    campus: str | None = None,
    scheduled_test_date: (
        date | None
    ) = None,
    requested_test_date: (
        date | None
    ) = None,
    *,
    runtime: ToolRuntime[
        SupportAgentContext
    ],
) -> dict[str, Any]:
    """
    Create a YouCode support request only after
    the visitor has explicitly confirmed consent.

    For test_reschedule, campus,
    scheduled_test_date and requested_test_date
    are mandatory.
    """

    context = runtime.context

    if not context.consent_confirmed:
        return {
            "status": (
                "consent_required"
            ),
            "message": (
                "Explicit consent is required "
                "before saving the request."
            ),
        }

    try:
        data = SupportRequestCreate(
            session_id=context.session_id,
            request_type=request_type,
            email=email,
            language=language,
            campus=campus,
            description=description,
            scheduled_test_date=(
                scheduled_test_date
            ),
            requested_test_date=(
                requested_test_date
            ),
        )

        with database_session() as session:
            service = (
                create_support_request_service(
                    session=session
                )
            )

            result = service.create_request(
                data
            )

        return {
            "status": "created",
            "request": result.model_dump(
                mode="json"
            ),
        }

    except (
        DomainError,
        ValidationError,
        ValueError,
    ) as error:
        return {
            "status": "rejected",
            "message": str(error),
        }

    except Exception:
        logger.exception(
            "Unexpected error while creating "
            "a support request."
        )

        return {
            "status": "error",
            "message": (
                "The support request could "
                "not be created."
            ),
        }


@tool
def process_test_rescheduling(
    reference: str,
    *,
    runtime: ToolRuntime[
        SupportAgentContext
    ],
) -> dict[str, Any]:
    """
    Process an existing test rescheduling
    request owned by the current visitor session.

    The tool searches official sessions and
    records a proposal requiring human approval.
    """

    try:
        with database_session() as session:
            service = (
                create_rescheduling_service(
                    session=session
                )
            )

            result = service.process(
                reference=reference,
                session_id=(
                    runtime.context.session_id
                ),
            )

        return {
            "status": "proposed",
            "proposal": result.model_dump(
                mode="json"
            ),
        }

    except DomainError as error:
        return {
            "status": "rejected",
            "message": str(error),
        }

    except Exception:
        logger.exception(
            "Unexpected error while processing "
            "a rescheduling request."
        )

        return {
            "status": "error",
            "message": (
                "The rescheduling request "
                "could not be processed."
            ),
        }


def create_support_tools() -> list:
    return [
        create_support_request,
        process_test_rescheduling,
    ]