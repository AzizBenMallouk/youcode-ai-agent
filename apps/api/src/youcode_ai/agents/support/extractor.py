import json

from datetime import date
from functools import lru_cache

from langchain_core.prompts import (
    ChatPromptTemplate,
)

from youcode_ai.agents.support.prompt import (
    CONSENT_EXTRACTION_HUMAN_TEMPLATE,
    CONSENT_EXTRACTION_SYSTEM_PROMPT,
    SUPPORT_EXTRACTION_HUMAN_TEMPLATE,
    SUPPORT_EXTRACTION_SYSTEM_PROMPT,
    SESSION_PROPOSAL_HUMAN_TEMPLATE,
    SESSION_PROPOSAL_SYSTEM_PROMPT,
)
from youcode_ai.agents.support.schemas import (
    ConsentExtraction,
    SupportInformationExtraction,
    SessionProposalDecision
)
from youcode_ai.core.llm import (
    create_chat_model,
)
from youcode_ai.orchestration.state import (
    SupportDraft,
)

class SupportExtractor:
    def __init__(self) -> None:
        chat_model = create_chat_model()

        information_prompt = (
            ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                        SUPPORT_EXTRACTION_SYSTEM_PROMPT,
                    ),
                    (
                        "human",
                        SUPPORT_EXTRACTION_HUMAN_TEMPLATE,
                    ),
                ]
            )
        )

        information_model = (
            chat_model.with_structured_output(
                SupportInformationExtraction
            )
        )

        self.information_chain = (
            information_prompt
            | information_model
        )

        consent_prompt = (
            ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                        CONSENT_EXTRACTION_SYSTEM_PROMPT,
                    ),
                    (
                        "human",
                        CONSENT_EXTRACTION_HUMAN_TEMPLATE,
                    ),
                ]
            )
        )

        consent_model = (
            chat_model.with_structured_output(
                ConsentExtraction
            )
        )

        self.consent_chain = (
            consent_prompt
            | consent_model
        )

        session_proposal_prompt = (
            ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                        SESSION_PROPOSAL_SYSTEM_PROMPT,
                    ),
                    (
                        "human",
                        SESSION_PROPOSAL_HUMAN_TEMPLATE,
                    ),
                ]
            )
        )

        session_proposal_model = (
            chat_model.with_structured_output(
                SessionProposalDecision
            )
        )

        self.session_proposal_chain = (
            session_proposal_prompt
            | session_proposal_model
        )

    def extract_information(
        self,
        *,
        message: str,
        current_draft: SupportDraft,
        current_date: date | None = None,
    ) -> SupportInformationExtraction:
        effective_date = (
            current_date
            or date.today()
        )

        serialized_draft = json.dumps(
            current_draft,
            ensure_ascii=False,
            default=str,
        )

        result = (
            self.information_chain.invoke(
                {
                    "current_date": (
                        effective_date
                        .isoformat()
                    ),
                    "current_draft": (
                        serialized_draft
                    ),
                    "message": message,
                }
            )
        )

        if not isinstance(
            result,
            SupportInformationExtraction,
        ):
            raise RuntimeError(
                "The support extractor returned "
                "an invalid information result."
            )

        return result

    def extract_consent(
        self,
        *,
        message: str,
    ) -> ConsentExtraction:
        result = (
            self.consent_chain.invoke(
                {
                    "message": message,
                }
            )
        )

        if not isinstance(
            result,
            ConsentExtraction,
        ):
            raise RuntimeError(
                "The support extractor returned "
                "an invalid consent result."
            )

        return result


    def extract_session_decision(
        self,
        *,
        message: str,
        proposed_test_date: str,
    ) -> SessionProposalDecision:
        result = (
            self.session_proposal_chain.invoke(
                {
                    "message": message,
                    "proposed_test_date": (
                        proposed_test_date
                    ),
                }
            )
        )

        if not isinstance(
            result,
            SessionProposalDecision,
        ):
            raise RuntimeError(
                "Invalid session proposal "
                "decision."
            )

        return result


@lru_cache(maxsize=1)
def create_support_extractor(
) -> SupportExtractor:
    return SupportExtractor()