from collections.abc import Mapping
from typing import Any, Literal
from shared.domain.enums import RequestType

MissingSupportField = Literal[
    "phone_number",
    "full_name",
    "cin",
    "request_type",
    "email",
    "campus",
    "scheduled_test_date",
    "requested_test_date",
    "description",
]

QUESTION_BY_FIELD: dict[str, str] = {
    "phone_number": "Quel est votre numéro de téléphone ?",
    "full_name": "Quel est votre nom complet ?",
    "cin": "Quel est votre numéro de CIN (Carte d'Identité Nationale) ?",
    "request_type": "Pouvez-vous préciser le problème que vous rencontrez ?",
    "email": "Quelle adresse e-mail avez-vous utilisée pour votre candidature ?",
    "campus": "Dans quel campus votre test est-il prévu : Safi, Youssoufia ou Nador ?",
    "scheduled_test_date": "Quelle est la date actuelle de votre test ?",
    "requested_test_date": "À partir de quelle date souhaitez-vous passer le test ?",
    "description": "Pouvez-vous décrire brièvement la raison de votre demande ?",
}

def get_missing_support_fields(
    draft: Mapping[str, Any],
) -> list[MissingSupportField]:
    """
    Retourne les informations nécessaires qui
    sont encore absentes ou invalides.
    """
    missing_fields: list[MissingSupportField] = []

    if not draft.get("phone_number"):
        missing_fields.append("phone_number")

    if not draft.get("full_name"):
        missing_fields.append("full_name")

    if not draft.get("cin"):
        missing_fields.append("cin")

    request_type = draft.get("request_type")

    if request_type is None:
        missing_fields.append("request_type")

    if not draft.get("email"):
        missing_fields.append("email")

    if request_type == RequestType.TEST_RESCHEDULE.value:
        if not draft.get("campus"):
            missing_fields.append("campus")

        if not draft.get("scheduled_test_date"):
            missing_fields.append("scheduled_test_date")

        if not draft.get("requested_test_date"):
            missing_fields.append("requested_test_date")

    if not draft.get("description"):
        missing_fields.append("description")

    return missing_fields

def get_support_question(
    field: MissingSupportField,
) -> str:
    return QUESTION_BY_FIELD[field]
