import json
from collections.abc import Mapping
from typing import Any

from langchain_core.messages import (
    HumanMessage,
    SystemMessage,
)

from youcode_ai.agents.newsletter.prompt import (
    NEWSLETTER_CONSENT_PROMPT,
    NEWSLETTER_EXTRACTION_PROMPT,
)
from youcode_ai.agents.newsletter.schemas import (
    NewsletterConsentDecision,
    NewsletterExtraction,
)
from youcode_ai.core.llm import (
    create_chat_model,
)


class NewsletterExtractor:
    def __init__(self) -> None:
        model = create_chat_model()

        self.extraction_model = (
            model.with_structured_output(
                NewsletterExtraction
            )
        )

        self.consent_model = (
            model.with_structured_output(
                NewsletterConsentDecision
            )
        )

    def extract(
        self,
        *,
        message: str,
        current_draft: Mapping[
            str,
            Any,
        ] | None = None,
    ) -> NewsletterExtraction:
        """
        Extrait les informations du nouveau
        message et les fusionne avec le brouillon.
        """

        clean_message = message.strip()

        if not clean_message:
            raise ValueError(
                "Newsletter message is empty."
            )

        draft = dict(
            current_draft or {}
        )

        payload = {
            "current_draft": draft,
            "new_message": clean_message[
                :4000
            ],
        }

        result = (
            self.extraction_model.invoke(
                [
                    SystemMessage(
                        content=(
                            NEWSLETTER_EXTRACTION_PROMPT
                        )
                    ),
                    HumanMessage(
                        content=json.dumps(
                            payload,
                            ensure_ascii=False,
                            default=str,
                        )
                    ),
                ]
            )
        )

        if not isinstance(
            result,
            NewsletterExtraction,
        ):
            raise RuntimeError(
                "Newsletter extraction returned "
                "an invalid result."
            )

        return self._merge_with_draft(
            current=draft,
            extracted=result,
        )

    def classify_consent(
        self,
        *,
        message: str,
    ) -> NewsletterConsentDecision:
        """
        Classe uniquement la réponse à la
        demande de consentement.
        """

        clean_message = message.strip()

        if not clean_message:
            return NewsletterConsentDecision(
                decision="unclear"
            )

        result = self.consent_model.invoke(
            [
                SystemMessage(
                    content=(
                        NEWSLETTER_CONSENT_PROMPT
                    )
                ),
                HumanMessage(
                    content=clean_message[
                        :1000
                    ]
                ),
            ]
        )

        if not isinstance(
            result,
            NewsletterConsentDecision,
        ):
            raise RuntimeError(
                "Newsletter consent classifier "
                "returned an invalid result."
            )

        return result

    @staticmethod
    def _merge_with_draft(
        *,
        current: dict[str, Any],
        extracted: NewsletterExtraction,
    ) -> NewsletterExtraction:
        """
        Évite de perdre les informations
        collectées lors des tours précédents.
        """

        extracted_data = (
            extracted.model_dump(
                mode="json"
            )
        )

        current_action = current.get(
            "action"
        )

        if (
            extracted_data["action"]
            == "unknown"
            and current_action
            in {
                "subscribe",
                "unsubscribe",
            }
        ):
            extracted_data["action"] = (
                current_action
            )

        if (
            not extracted_data.get("email")
            and current.get("email")
        ):
            extracted_data["email"] = (
                current["email"]
            )

        if (
            extracted_data.get("language")
            == "fr"
            and current.get("language")
            in {
                "en",
                "ar",
                "darija",
            }
        ):
            extracted_data["language"] = (
                current["language"]
            )

        current_topics = current.get(
            "topics",
            [],
        )

        extracted_topics = (
            extracted_data.get(
                "topics",
                [],
            )
        )

        # Les préférences mentionnées dans
        # plusieurs messages sont cumulées.
        extracted_data["topics"] = list(
            dict.fromkeys(
                [
                    *current_topics,
                    *extracted_topics,
                ]
            )
        )

        return NewsletterExtraction(
            **extracted_data
        )


def create_newsletter_extractor(
) -> NewsletterExtractor:
    return NewsletterExtractor()