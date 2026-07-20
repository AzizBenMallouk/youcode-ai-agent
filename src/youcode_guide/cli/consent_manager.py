from dataclasses import dataclass, field

from youcode_guide.metier.services.consent_service import (
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


POSITIVE_ANSWERS = {
    "oui",
    "o",
    "yes",
    "y",
    "je confirme",
    "je confirme mon consentement",
    "j'accepte",
    "نعم",
    "اه",
    "آه",
}


NEGATIVE_ANSWERS = {
    "non",
    "n",
    "no",
    "je refuse",
    "je n'accepte pas",
    "لا",
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
            "Ces données seront utilisées uniquement "
            "pour cet objectif."
        )

        while True:
            confirmation = input(
                "\nConfirmez-vous votre consentement ? "
                "(oui/non) : "
            ).strip().lower()

            if confirmation in POSITIVE_ANSWERS:
                token = self.consent_service.create_grant(
                    session_id=session_id,
                    email=email,
                    purpose=purpose,
                )

                self.tokens[purpose] = token

                print(
                    "\nConsentement confirmé. "
                    "Traitement de la demande...\n"
                )

                return True

            if confirmation in NEGATIVE_ANSWERS:
                print(
                    "\nConsentement refusé. "
                    "Aucune donnée personnelle n'a été "
                    "enregistrée.\n"
                )

                return False

            print(
                "\nRéponse non reconnue. "
                "Veuillez répondre par oui ou non."
            )