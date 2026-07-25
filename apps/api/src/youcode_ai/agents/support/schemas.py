from datetime import date
from typing import Literal

from pydantic import (
    BaseModel,
    Field,
)
from youcode_ai.domain.enums import (
    Language,
)


class SessionProposalDecision(BaseModel):
    decision: Literal[
        "accepted",
        "refused",
        "unclear",
    ]

    evidence: str | None = None


class SupportInformationExtraction(BaseModel):
    """
    Informations extraites du dernier message
    du visiteur.

    Une valeur absente du message doit être None.
    """

    request_type: str | None = Field(
        default=None,
        description=(
            "Type de demande détecté dans le "
            "message. Null si le type ne peut "
            "pas être déterminé."
        ),
    )

    language: str = Field(
        description=("Langue dominante du message : fr, en, ar ou darija."),
    )

    email: str | None = Field(
        default=None,
        description=("Adresse email explicitement présente dans le message."),
    )

    phone_number: str | None = Field(
        default=None,
        description=("Numéro de téléphone (ex: 06..., +212...) explicitement présent dans le message."),
    )

    full_name: str | None = Field(
        default=None,
        description=("Nom complet explicitement présent dans le message."),
    )

    cin: str | None = Field(
        default=None,
        description=("Numéro de CIN / Carte d'Identité explicitement présent dans le message."),
    )

    campus: str | None = Field(
        default=None,
        description=(
            "Campus explicitement mentionné. "
            "Valeurs habituelles : Safi, "
            "Youssoufia ou Nador."
        ),
    )

    scheduled_test_date: date | None = Field(
        default=None,
        description=("Date actuelle du test du candidat. Null si absente ou ambiguë."),
    )

    requested_test_date: date | None = Field(
        default=None,
        description=(
            "Date souhaitée ou date à partir de laquelle le candidat est disponible."
        ),
    )

    description: str | None = Field(
        default=None,
        max_length=2000,
        description=(
            "Description ou motif du problème explicitement donné par le visiteur."
        ),
    )

    ambiguities: list[str] = Field(
        default_factory=list,
        description=(
            "Liste des informations ambiguës qui nécessitent une clarification."
        ),
    )


class ConsentExtraction(BaseModel):
    """
    Classification de la réponse donnée à une
    demande explicite de consentement.
    """

    decision: Literal[
        "accepted",
        "refused",
        "unclear",
    ] = Field(
        description=(
            "accepted uniquement pour un accord "
            "explicite, refused pour un refus "
            "explicite, sinon unclear."
        ),
    )

    evidence: str | None = Field(
        default=None,
        description=("Courte partie de la réponse qui justifie la classification."),
    )


class SupportWorkflowResponse(BaseModel):
    """
    Réponse finale produite par le workflow
    Support pour le frontend.
    """

    status: Literal[
        "collecting",
        "awaiting_consent",
        "awaiting_session_confirmation",
        "created",
        "proposed",
        "cancelled",
        "requires_human",
        "error",
    ]

    proposed_test_date: str | None = None

    language: Language

    answer: str

    request_reference: str | None = None

    requires_human: bool = False
