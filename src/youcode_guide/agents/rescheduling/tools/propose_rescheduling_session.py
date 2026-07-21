import json
from datetime import date
from typing import Any
from youcode_guide.agents.shared.helpers.serialize_error import serialize_error

from langchain_core.tools import (
    BaseTool,
    tool,
)

from youcode_guide.database.sqlite.connection import (
    create_database_session,
)
from youcode_guide.metier.exceptions.rescheduling import (
    InvalidReschedulingRequest,
    ProposedSessionNotAvailable,
    ReschedulingAlreadyProcessed,
    ReschedulingRequestNotFound,
)
from youcode_guide.metier.services.rescheduling_service import (
    create_rescheduling_service,
)

import logging


logger = logging.getLogger(__name__)



@tool
def propose_rescheduling_session(
    reference: str,
    external_session_id: str,
    decision_reason: str,
) -> str:
    """
    Enregistre une proposition de nouvelle
    session pour une demande de report.

    L'identifiant doit obligatoirement provenir
    de prepare_rescheduling_request.

    La session sera vérifiée à nouveau auprès de
    l'API officielle.

    Ne jamais inventer un identifiant.
    """
    session = create_database_session()

    try:
        service = create_rescheduling_service(
            session=session,
        )

        request = service.propose_session(
            reference=reference,
            external_session_id=(
                external_session_id
            ),
            decision_reason=decision_reason,
        )

        session.commit()

        return json.dumps(
            {
                "success": True,
                "reference": (
                    request.reference
                ),
                "status": request.status,
                "external_session_id": (
                    request
                    .external_session_id
                ),
                "proposed_test_date": (
                    request
                    .proposed_test_date
                    .isoformat()
                    if request
                    .proposed_test_date
                    else None
                ),
                "requires_human": True,
                "message": (
                    "La proposition attend "
                    "une validation humaine."
                ),
            },
            ensure_ascii=False,
        )

    except ProposedSessionNotAvailable:
        session.rollback()

        return serialize_error(
            code="SESSION_NOT_AVAILABLE",
            message=(
                "La session sélectionnée "
                "n'est plus disponible."
            ),
        )

    except Exception as error:
        session.rollback()

        logger.exception(
            "Unable to propose session "
            "for request %s.",
            reference,
        )

        return serialize_error(
            code="TECHNICAL_ERROR",
            message=(
                f"{type(error).__name__}: "
                f"{error}"
            ),
        )

    finally:
        session.close()