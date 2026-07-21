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
def prepare_rescheduling_request(
    reference: str,
    date_from: date | None = None,
    date_to: date | None = None,
) -> str:
    """
    Prépare le traitement d'une demande de
    report de test.

    Vérifie la demande dans la base et récupère
    les prochaines sessions officielles depuis
    l'API externe.

    Utiliser la référence officielle de la
    demande. Ne jamais inventer une référence,
    une date ou un identifiant de session.
    """

    session = create_database_session()

    try:
        service = create_rescheduling_service(
            session=session,
        )

        context = service.prepare_request(
            reference=reference,
            date_from=date_from,
            date_to=date_to,
        )

        session.commit()

        return context.model_dump_json()

    except ReschedulingRequestNotFound:
        session.rollback()

        return serialize_error(
            code="REQUEST_NOT_FOUND",
            message=(
                "La demande de report "
                "est introuvable."
            ),
        )

    except InvalidReschedulingRequest as error:
        session.rollback()

        return serialize_error(
            code="INVALID_REQUEST",
            message=str(error),
        )

    except ReschedulingAlreadyProcessed:
        session.rollback()

        return serialize_error(
            code="REQUEST_ALREADY_CLOSED",
            message=(
                "La demande a déjà été traitée."
            ),
        )

    # except Exception:
    #     session.rollback()

    #     return serialize_error(
    #         code="TECHNICAL_ERROR",
    #         message=(
    #             "Une erreur technique est "
    #             "survenue pendant la préparation."
    #         ),
    #     )
    except Exception as error:
        session.rollback()

        logger.exception(
            "Unable to prepare rescheduling "
            "request %s.",
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




