from dataclasses import dataclass, field

from youcode_guide.consent.service import (
    ConsentService,
)


PURPOSE_LABELS = {
    "waitlist": (
        "enregistrer votre adresse email afin de vous "
        "contacter lors de l'ouverture des inscriptions"
    ),
    "access_support": (
        "enregistrer vos informations afin qu'un responsable "
        "puisse vous aider avec votre problème d'accès"
    ),
    "test_reschedule": (
        "enregistrer votre demande afin qu'un responsable "
        "puisse étudier le report de votre test"
    ),
}


@dataclass
class TerminalConsentManager:
    consent_service: ConsentService

    tokens: dict[str, str] = field(
        default_factory=dict,
    )

    def request_consent(
        self,
        *,
        session_id: str,
        email: str,
        purpose: str,
    ) -> bool:
        explanation = PURPOSE_LABELS.get(
            purpose,
            "traiter votre demande",
        )

        print("\nConsentement requis")
        print(f"Adresse concernée : {email}")
        print(f"Objectif : {explanation}.")
        print(
            "Vos données seront utilisées uniquement "
            "pour cet objectif."
        )

        confirmation = input(
            "Acceptez-vous ? (oui/non) : "
        ).strip().lower()

        if confirmation not in {
            "oui",
            "o",
            "yes",
            "y",
            "نعم",
            "اه",
            "آه",
        }:
            print(
                "\nAucune donnée personnelle n'a été "
                "enregistrée.\n"
            )
            return False

        token = self.consent_service.create_grant(
            session_id=session_id,
            email=email,
            purpose=purpose,
        )

        self.tokens[purpose] = token

        return True