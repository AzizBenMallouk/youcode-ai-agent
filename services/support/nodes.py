from datetime import date

from langchain_core.messages import (
    AIMessage,
    HumanMessage,
)
from pydantic import (
    EmailStr,
    TypeAdapter,
    ValidationError,
)
from typing import Any
from .extractor import (
    SupportExtractor,
    create_support_extractor,
)
from .validator import (
    get_missing_support_fields,
    get_support_question,
)
from .schemas import (
    SupportWorkflowResponse,
)
from shared.application.schemas import (
    SupportRequestCreate,
)

from shared.domain.enums import (
    Language,
    RequestType,
)
from shared.domain.exceptions import (
    DomainError,
)

from .state import (
    SupportDraft,
    SupportState,
)

EMAIL_ADAPTER = TypeAdapter(EmailStr)

class SupportNodes:
    def __init__(
        self,
        *,
        extractor: (SupportExtractor | None) = None,
    ) -> None:
        self.extractor = extractor or create_support_extractor()

    def extract_information(
        self,
        state: SupportState,
    ) -> dict:
        """
        Utilise le LLM pour extraire les
        informations du dernier message.
        """

        message = self._get_last_user_message(state)

        current_draft: SupportDraft = dict(
            state.get(
                "support_draft",
                {},
            )
        )

        extraction = self.extractor.extract_information(
            message=message,
            current_draft=(current_draft),
        )

        extracted_values = extraction.model_dump(
            exclude_none=True,
            mode="json",
        )

        updated_draft: SupportDraft = {
            **current_draft,
            **extracted_values,
        }

        # Auto-extract phone number from user_id
        user_id = state.get("user_id", "")
        if user_id:
            updated_draft["phone_number"] = user_id.split("@")[0] if "@" in user_id else user_id

        ambiguities = list(
            updated_draft.get(
                "ambiguities",
                [],
            )
        )

        email = updated_draft.get("email")

        if email and not self._is_valid_email(email):
            updated_draft.pop(
                "email",
                None,
            )

            ambiguities.append("L’adresse e-mail fournie n’est pas valide.")

        scheduled_date = updated_draft.get("scheduled_test_date")

        requested_date = updated_draft.get("requested_test_date")

        if scheduled_date and requested_date:
            scheduled_date = date.fromisoformat(scheduled_date)

            requested_date = date.fromisoformat(requested_date)

            if requested_date <= scheduled_date:
                updated_draft.pop(
                    "requested_test_date",
                    None,
                )

                ambiguities.append(
                    "La nouvelle date doit être postérieure à la date actuelle du test."
                )

        updated_draft["ambiguities"] = ambiguities

        return {
            "active_agent": "support",
            "support_phase": "collecting",
            "support_draft": (updated_draft),
            "consent_confirmed": False,
            "final_response": None,
            "requires_human": False,
        }

    def request_missing_information(
        self,
        state: SupportState,
    ) -> dict:
        """
        Cherche les informations manquantes.

        Pose une question ou demande le
        consentement si tout est complet.
        """

        draft = state.get(
            "support_draft",
            {},
        )

        missing_fields = get_missing_support_fields(draft)

        if missing_fields:
            field_name = missing_fields[0]

            answer = get_support_question(field_name)

            return self._answer_update(
                state=state,
                status="collecting",
                answer=answer,
                support_phase="collecting",
            )

        answer = self._create_consent_message(draft)

        return self._answer_update(
            state=state,
            status="awaiting_consent",
            answer=answer,
            support_phase=("awaiting_consent"),
        )

    def classify_consent(
        self,
        state: SupportState,
    ) -> dict:
        """
        Analyse le dernier message uniquement
        lorsque le consentement a été demandé.
        """

        message = self._get_last_user_message(state)

        extraction = self.extractor.extract_consent(message=message)

        if extraction.decision == "accepted":
            return {
                "active_agent": "support",
                "support_phase": "processing",
                "consent_confirmed": True,
                "final_response": None,
                "requires_human": False,
            }

        if extraction.decision == "refused":
            answer = "Votre demande n’a pas été enregistrée."

            return self._answer_update(
                state=state,
                status="cancelled",
                answer=answer,
                support_phase="cancelled",
                active_agent=None,
            )

        answer = (
            "Je dois obtenir une réponse claire. "
            "Acceptez-vous que ces informations "
            "soient enregistrées et utilisées "
            "pour traiter votre demande ? "
            "Répondez par oui ou non."
        )

        return self._answer_update(
            state=state,
            status="awaiting_consent",
            answer=answer,
            support_phase=("awaiting_consent"),
        )

    async def process_request(
        self,
        state: SupportState,
    ) -> dict[str, Any]:
        """
        Crée le consentement et la demande SQL.

        Pour un report, recherche également une
        session officielle disponible.
        """

        if not state.get(
            "consent_confirmed",
            False,
        ):
            answer = (
                "Le consentement est nécessaire avant l’enregistrement de la demande."
            )

            return self._answer_update(
                state=state,
                status="awaiting_consent",
                answer=answer,
                support_phase=("awaiting_consent"),
            )

        draft = state.get(
            "support_draft",
            {},
        )

        try:
            request_data = SupportRequestCreate(
                session_id=state["session_id"],
                request_type=draft["request_type"],
                email=draft["email"],
                language=draft.get(
                    "language",
                    Language.FR.value,
                ),
                campus=draft.get("campus"),
                description=draft["description"],
                scheduled_test_date=(draft.get("scheduled_test_date")),
                requested_test_date=(draft.get("requested_test_date")),
                phone_number=draft.get("phone_number"),
                full_name=draft.get("full_name"),
                cin=draft.get("cin"),
            )


            from shared.infrastructure.database.connection import database_session
            from shared.infrastructure.database.tables.visitor_request import VisitorRequest
            import uuid
            
            ref = str(uuid.uuid4())[:8]
            
            with database_session() as db:
                new_request = VisitorRequest(
                    reference=ref,
                    user_id=state.get("session_id", ""),
                    first_name=draft.get("full_name", "").split(" ")[0] if draft.get("full_name") else "",
                    last_name=" ".join(draft.get("full_name", "").split(" ")[1:]) if draft.get("full_name") else "",
                    email=draft["email"],
                    cin=draft.get("cin", ""),
                    campus=draft.get("campus", ""),
                    intent=draft["request_type"],
                    details={
                        "description": draft["description"],
                        "old_date": draft.get("scheduled_test_date", ""),
                        "new_date": draft.get("requested_test_date", "")
                    }
                )
                db.add(new_request)

            if draft["request_type"] == RequestType.TEST_RESCHEDULE.value:
                # We mock the rescheduling for now since it depended on Postgres
                proposed_date = date.today() # Mock date
                formatted_date = proposed_date.strftime("%d/%m/%Y à %H:%M")

                answer = (
                    "Votre demande a été enregistrée "
                    f"avec la référence {ref}. "
                    "La prochaine session disponible "
                    f"est prévue le {formatted_date}. "
                    "Cette date vous convient-elle ? "
                    "Répondez par oui ou non. "
                    "Si elle ne vous convient pas, "
                    "je rechercherai une autre session."
                )

                return self._answer_update(
                    state=state,
                    status="awaiting_session_confirmation",
                    answer=answer,
                    support_phase="awaiting_session_confirmation",
                    active_agent="support",
                    request_reference=ref,
                    proposed_session_id="mock-session-id",
                    proposed_test_date=proposed_date.isoformat(),
                    requires_human=False,
                )

            answer = (
                "Votre demande a été "
                "enregistrée avec la référence "
                f"{ref}. "
                "Elle sera transmise à un "
                    "responsable."
                )

            return self._answer_update(
                state=state,
                status="requires_human",
                answer=answer,
                support_phase="completed",
                active_agent=None,
                request_reference=ref,
                requires_human=True,
            )

        except (
            DomainError,
            ValidationError,
            KeyError,
            ValueError,
        ):
            raise

        except Exception:
            raise

    def classify_session_proposal(
        self,
        state: SupportState,
    ) -> dict:
        message = self._get_last_user_message(state)

        decision = self.extractor.extract_session_decision(
            message=message,
            proposed_test_date=state["proposed_test_date"],
        )

        if decision.decision == "accepted":
            return {
                "support_phase": ("confirming_session"),
            }

        if decision.decision == "refused":
            rejected_ids = list(
                state.get(
                    "rejected_session_ids",
                    [],
                )
            )

            current_session_id = state.get("proposed_session_id")

            if current_session_id and current_session_id not in rejected_ids:
                rejected_ids.append(current_session_id)

            return {
                "support_phase": ("searching_alternative"),
                "rejected_session_ids": (rejected_ids),
            }

        answer = "Cette date vous convient-elle ? Répondez par oui ou non."

        return self._answer_update(
            state=state,
            status=("awaiting_session_confirmation"),
            answer=answer,
            support_phase=("awaiting_session_confirmation"),
        )

    async def confirm_session_proposal(
        self,
        state: SupportState,
    ) -> dict:
        # Mock database update for now
        proposed_date = date.today().strftime("%d/%m/%Y à %H:%M")
        reference = state.get("request_reference", "MOCK123")
        
        draft = state.get("support_draft", {})
        email = draft.get("email")
        old_date = draft.get("scheduled_test_date", "Date Inconnue")
        campus = draft.get("campus", "Campus Inconnu")

        if email:
            from shared.mcp.client import call_agent_tool
            from shared.core.config import settings
            target_url = getattr(settings, "email_mcp_url", "http://email-mcp:8005")
            
            await call_agent_tool(
                agent_base_url=target_url,
                tool_name="send_rescheduling_email",
                email=email,
                old_date=old_date,
                new_date=proposed_date,
                campus=campus
            )

        answer = (
            f"La date du {proposed_date} a été "
            "acceptée. Un email de confirmation "
            "vous a été envoyé. Votre demande attend "
            "maintenant une validation humaine. "
            f"Référence : {reference}."
        )

        return self._answer_update(
            state=state,
            status="proposed",
            answer=answer,
            support_phase="completed",
            active_agent=None,
            request_reference=reference,
            proposed_test_date=date.today().isoformat(),
            requires_human=True,
        )

    def search_alternative_session(
        self,
        state: SupportState,
    ) -> dict:
        # Mock alternative searching
        proposed_date = date.today().strftime("%d/%m/%Y à %H:%M")
        reference = state.get("request_reference", "MOCK123")

        answer = (
            "Une autre session est disponible "
            f"le {proposed_date}. "
            "Cette nouvelle date vous "
            "convient-elle ? Répondez par "
            "oui ou non."
        )

        return self._answer_update(
            state=state,
            status=("awaiting_session_confirmation"),
            answer=answer,
            support_phase=("awaiting_session_confirmation"),
            active_agent="support",
            request_reference=reference,
            proposed_session_id="mock-alternative-id",
            proposed_test_date=date.today().isoformat(),
            requires_human=False,
        )


    @staticmethod
    def _get_last_user_message(
        state: SupportState,
    ) -> str:
        for message in reversed(state.get("messages", [])):
            if isinstance(
                message,
                HumanMessage,
            ):
                return str(message.content).strip()

        raise ValueError("No user message was found.")

    @staticmethod
    def _is_valid_email(
        email: str,
    ) -> bool:
        try:
            EMAIL_ADAPTER.validate_python(email)
        except ValidationError:
            return False

        return True

    @staticmethod
    def _create_consent_message(
        draft: SupportDraft,
    ) -> str:
        request_type = draft.get("request_type")

        email = draft.get("email")

        if request_type == RequestType.TEST_RESCHEDULE.value:
            campus = draft.get("campus")

            scheduled_date = date.fromisoformat(draft.get("scheduled_test_date"))

            requested_date = date.fromisoformat(draft.get("requested_test_date"))

            return (
                "Récapitulatif : votre demande "
                f"concerne le campus de {campus}, "
                f"avec un test prévu le "
                f"{scheduled_date:%d/%m/%Y} et "
                f"une nouvelle date souhaitée à "
                f"partir du "
                f"{requested_date:%d/%m/%Y}. "
                f"L’adresse utilisée est {email}. "
                "Acceptez-vous que ces "
                "informations soient enregistrées "
                "et utilisées pour traiter votre "
                "demande ? Répondez par oui "
                "ou non."
            )

        return (
            "Récapitulatif : votre demande de "
            f"support sera associée à {email}. "
            "Acceptez-vous que ces informations "
            "soient enregistrées et utilisées "
            "pour traiter votre demande ? "
            "Répondez par oui ou non."
        )

    @staticmethod
    def _answer_update(
        *,
        state: SupportState,
        status: str,
        answer: str,
        support_phase: str,
        active_agent: str | None = ("support"),
        request_reference: (str | None) = None,
        requires_human: bool = False,
        proposed_test_date: (str | None) = None,
        proposed_session_id: (str | None) = None,
    ) -> dict:
        language = state.get(
            "support_draft",
            {},
        ).get(
            "language",
            Language.FR,
        )

        response = SupportWorkflowResponse(
            status=status,
            language=language,
            answer=answer,
            request_reference=(request_reference),
            requires_human=(requires_human),
            proposed_test_date=(proposed_test_date),
        )

        return {
            "messages": [AIMessage(content=answer)],
            "active_agent": active_agent,
            "support_phase": support_phase,
            "request_reference": (request_reference),
            "final_response": (response.model_dump(mode="json")),
            "requires_human": (requires_human),
            "proposed_test_date": (proposed_test_date),
            "proposed_session_id": (proposed_session_id),
            "rejected_session_ids": (
                state.get(
                    "rejected_session_ids",
                    [],
                )
            ),
        }


def create_support_nodes() -> SupportNodes:
    return SupportNodes()
