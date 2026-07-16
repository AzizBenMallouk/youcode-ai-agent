from uuid import uuid4

from youcode_guide.agent.service import (
    YouCodeAgentService,
)
from youcode_guide.cli.consent_manager import (
    TerminalConsentManager,
)
from youcode_guide.consent.service import (
    create_consent_service,
)


class TerminalApplication:
    def __init__(self) -> None:
        self.session_id = str(uuid4())

        self.agent_service = YouCodeAgentService()

        self.consent_manager = TerminalConsentManager(
            consent_service= create_consent_service(),
        )

    def run(self) -> None:
        self._show_welcome_message()

        while True:
            question = input("Vous : ").strip()

            if question.lower() in {
                "quit",
                "exit",
                "quitter",
            }:
                print("\nÀ bientôt.")
                break

            if not question:
                continue

            try:
                self._process_question(question)

            except Exception:
                print(
                    "\nUne erreur technique est survenue. "
                    "Veuillez réessayer.\n"
                )

    def _process_question(
        self,
        question: str,
    ) -> None:
        result = self.agent_service.ask(
            session_id=self.session_id,
            question=question,
            consent_tokens=self.consent_manager.tokens,
        )

        print(f"\nGuide : {result.response.answer}\n")

        pending = result.pending_consent

        if pending is None:
            return

        accepted = self.consent_manager.request_consent(
            session_id=self.session_id,
            email=pending.email,
            purpose=pending.purpose,
        )

        if not accepted:
            return

        self._continue_after_consent(
            purpose=pending.purpose,
        )

    def _continue_after_consent(
        self,
        *,
        purpose: str,
    ) -> None:
        continuation_message = (
            "Le visiteur vient de confirmer explicitement "
            f"son consentement pour l'objectif '{purpose}'. "
            "Reprends maintenant la demande précédente et "
            "appelle le tool correspondant. N'invente aucune "
            "information manquante."
        )

        result = self.agent_service.ask(
            session_id=self.session_id,
            question=continuation_message,
            consent_tokens=self.consent_manager.tokens,
        )

        print(f"\nGuide : {result.response.answer}\n")

        # Le consentement est utilisable une seule fois.
        self.consent_manager.tokens.pop(
            purpose,
            None,
        )

    @staticmethod
    def _show_welcome_message() -> None:
        print("\nYouCode AI Guide")
        print(
            "Posez vos questions concernant YouCode."
        )
        print(
            "Tapez 'quit' pour terminer.\n"
        )


def main() -> None:
    application = TerminalApplication()
    application.run()


if __name__ == "__main__":
    main()