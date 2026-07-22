import logging
from typing import Any

from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
)

from youcode_ai.agents.newsletter.extractor import (
    NewsletterExtractor,
)
from youcode_ai.agents.newsletter.validator import (
    get_missing_newsletter_fields,
    get_newsletter_question,
    normalize_email,
)
from youcode_ai.application.services.newsletter import (
    NewsletterService,
)
from youcode_ai.infrastructure.database.connection import (
    database_session,
)
from youcode_ai.orchestration.state import (
    YouCodeState,
)


logger = logging.getLogger(__name__)


class NewsletterNodes:
    def __init__(
        self,
        extractor: NewsletterExtractor,
    ) -> None:
        self.extractor = extractor

    def extract(
        self,
        state: YouCodeState,
    ) -> dict[str, Any]:
        """
        Extrait et valide les informations du
        visiteur.
        """

        message = self._last_user_message(
            state.get("messages", [])
        )

        if not message:
            return self._error(
                "Veuillez écrire votre demande."
            )

        try:
            extraction = self.extractor.extract(
                message=message,
                current_draft=state.get(
                    "newsletter_draft",
                    {},
                ),
            )

            draft = extraction.model_dump(
                mode="json",
                exclude_none=True,
            )

            normalized_email = normalize_email(
                draft.get("email")
            )

            if normalized_email:
                draft["email"] = (
                    normalized_email
                )

            missing = (
                get_missing_newsletter_fields(
                    draft
                )
            )

            language = draft.get(
                "language",
                "fr",
            )

            if missing:
                answer = get_newsletter_question(
                    field=missing[0],
                    language=language,
                )

                return self._answer(
                    answer=answer,
                    language=language,
                    status="collecting",
                    newsletter_phase=(
                        "collecting"
                    ),
                    newsletter_draft=draft,
                )

            action = draft["action"]

            # Une désinscription ne nécessite
            # pas de consentement marketing.
            if action == "unsubscribe":
                return {
                    "active_agent": (
                        "newsletter"
                    ),
                    "newsletter_phase": (
                        "processing"
                    ),
                    "newsletter_draft": draft,
                    "newsletter_consent_confirmed": (
                        False
                    ),
                    "requires_human": False,
                }

            answer = (
                self._consent_question(
                    language=language,
                    email=draft["email"],
                    topics=draft["topics"],
                )
            )

            return self._answer(
                answer=answer,
                language=language,
                status="awaiting_consent",
                newsletter_phase=(
                    "awaiting_consent"
                ),
                newsletter_draft=draft,
                newsletter_consent_confirmed=(
                    False
                ),
            )

        except Exception:
            logger.exception(
                "Newsletter extraction failed."
            )

            return self._technical_error()

    def consent(
        self,
        state: YouCodeState,
    ) -> dict[str, Any]:
        """
        Analyse la réponse oui/non du visiteur.
        """

        message = self._last_user_message(
            state.get("messages", [])
        )

        draft = state.get(
            "newsletter_draft",
            {},
        )

        language = draft.get(
            "language",
            "fr",
        )

        try:
            decision = (
                self.extractor
                .classify_consent(
                    message=message or "",
                )
            )

            if decision.decision == "accepted":
                return {
                    "active_agent": (
                        "newsletter"
                    ),
                    "newsletter_phase": (
                        "processing"
                    ),
                    "newsletter_consent_confirmed": (
                        True
                    ),
                    "requires_human": False,
                }

            if decision.decision == "refused":
                answer = self._cancelled_answer(
                    language
                )

                return self._answer(
                    answer=answer,
                    language=language,
                    status="cancelled",
                    newsletter_phase=(
                        "cancelled"
                    ),
                    newsletter_consent_confirmed=(
                        False
                    ),
                )

            answer = self._unclear_consent_answer(
                language
            )

            return self._answer(
                answer=answer,
                language=language,
                status="awaiting_consent",
                newsletter_phase=(
                    "awaiting_consent"
                ),
                newsletter_consent_confirmed=(
                    False
                ),
            )

        except Exception:
            logger.exception(
                "Newsletter consent "
                "classification failed."
            )

            return self._technical_error()

    def process(
        self,
        state: YouCodeState,
    ) -> dict[str, Any]:
        """
        Enregistre l'inscription ou la
        désinscription dans une transaction SQL.
        """

        draft = state.get(
            "newsletter_draft",
            {},
        )

        action = draft.get("action")
        email = draft.get("email")
        language = draft.get(
            "language",
            "fr",
        )

        if not email:
            return self._technical_error()

        try:
            with database_session() as session:
                service = NewsletterService(
                    session=session
                )

                if action == "subscribe":
                    result = service.subscribe(
                        session_id=state.get(
                            "session_id",
                            "",
                        ),
                        email=email,
                        language=language,
                        topics=draft.get(
                            "topics",
                            [],
                        ),
                        consent_confirmed=state.get(
                            "newsletter_consent_confirmed",
                            False,
                        ),
                    )

                    answer = (
                        self._subscribed_answer(
                            language
                        )
                    )

                elif action == "unsubscribe":
                    result = service.unsubscribe(
                        email=email
                    )

                    answer = (
                        self._unsubscribed_answer(
                            language
                        )
                    )

                else:
                    return self._technical_error()

            return {
                "active_agent": "newsletter",
                "newsletter_phase": "completed",
                "subscription_reference": (
                    result.reference
                ),
                "requires_human": False,
                "messages": [
                    AIMessage(
                        content=answer
                    )
                ],
                "final_response": {
                    "status": result.status,
                    "language": language,
                    "answer": answer,
                    "subscription_reference": (
                        result.reference
                    ),
                    "requires_human": False,
                },
            }

        except Exception:
            logger.exception(
                "Newsletter processing failed."
            )

            return self._technical_error()

    @staticmethod
    def _last_user_message(
        messages: list[BaseMessage],
    ) -> str | None:
        for message in reversed(messages):
            if isinstance(
                message,
                HumanMessage,
            ):
                if isinstance(
                    message.content,
                    str,
                ):
                    content = (
                        message.content.strip()
                    )

                    if content:
                        return content

        return None

    @staticmethod
    def _answer(
        *,
        answer: str,
        language: str,
        status: str,
        newsletter_phase: str,
        **updates: Any,
    ) -> dict[str, Any]:
        return {
            "active_agent": "newsletter",
            "newsletter_phase": (
                newsletter_phase
            ),
            "requires_human": False,
            "messages": [
                AIMessage(
                    content=answer
                )
            ],
            "final_response": {
                "status": status,
                "language": language,
                "answer": answer,
                "subscription_reference": None,
                "requires_human": False,
            },
            **updates,
        }

    @staticmethod
    def _consent_question(
        *,
        language: str,
        email: str,
        topics: list[str],
    ) -> str:
        topic_names = {
            "full_program_registration": (
                "inscriptions"
            ),
            "bootcamps": "bootcamps",
            "events": "événements",
            "youcode_news": "actualités YouCode",
        }

        displayed_topics = ", ".join(
            topic_names.get(topic, topic)
            for topic in topics
        )

        if language == "en":
            return (
                f"Do you agree that YouCode uses "
                f"{email} to send you notifications "
                f"about: {displayed_topics}? "
                "Please answer yes or no."
            )

        return (
            f"Acceptez-vous que YouCode utilise "
            f"l'adresse {email} pour vous envoyer "
            f"des notifications concernant : "
            f"{displayed_topics} ? "
            "Répondez par oui ou non."
        )

    @staticmethod
    def _cancelled_answer(
        language: str,
    ) -> str:
        if language == "en":
            return (
                "Your subscription has been "
                "cancelled. No information was "
                "registered."
            )

        return (
            "Votre inscription a été annulée. "
            "Aucune information n'a été "
            "enregistrée."
        )

    @staticmethod
    def _unclear_consent_answer(
        language: str,
    ) -> str:
        if language == "en":
            return (
                "Please confirm whether you agree "
                "to receive these notifications "
                "(yes/no)."
            )

        return (
            "Confirmez-vous que vous acceptez de "
            "recevoir ces notifications "
            "(oui/non) ?"
        )

    @staticmethod
    def _subscribed_answer(
        language: str,
    ) -> str:
        if language == "en":
            return (
                "Your notification preferences "
                "have been registered."
            )

        return (
            "Vos préférences de notification ont "
            "bien été enregistrées."
        )

    @staticmethod
    def _unsubscribed_answer(
        language: str,
    ) -> str:
        if language == "en":
            return (
                "Your request to stop receiving "
                "notifications has been processed."
            )

        return (
            "Votre demande de désinscription aux "
            "notifications a bien été traitée."
        )

    @classmethod
    def _technical_error(
        cls,
    ) -> dict[str, Any]:
        return cls._answer(
            answer=(
                "Une erreur technique est "
                "survenue. Veuillez réessayer."
            ),
            language="fr",
            status="error",
            newsletter_phase="cancelled",
        )

    @classmethod
    def _error(
        cls,
        answer: str,
    ) -> dict[str, Any]:
        return cls._answer(
            answer=answer,
            language="fr",
            status="collecting",
            newsletter_phase="collecting",
        )


def create_newsletter_nodes(
) -> NewsletterNodes:
    return NewsletterNodes(
        extractor=NewsletterExtractor()
    )