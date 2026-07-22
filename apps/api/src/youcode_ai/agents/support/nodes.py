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

from youcode_ai.agents.support.extractor import (
    SupportExtractor,
    create_support_extractor,
)
from youcode_ai.agents.support.schemas import (
    SupportWorkflowResponse,
)
from youcode_ai.application.schemas import (
    SupportRequestCreate,
)
from youcode_ai.application.services import (
    create_rescheduling_service,
    create_support_request_service,
)
from youcode_ai.domain.enums import (
    Language,
    RequestType,
)
from youcode_ai.domain.exceptions import (
    DomainError,
)
from youcode_ai.infrastructure.database import (
    database_session,
)
from youcode_ai.orchestration.state import (
    SupportDraft,
    YouCodeState,
)


EMAIL_ADAPTER = TypeAdapter(
    EmailStr
)


QUESTION_BY_FIELD = {
    "request_type": (
        "Pouvez-vous préciser le problème "
        "que vous rencontrez ?"
    ),
    "email": (
        "Quelle adresse e-mail avez-vous "
        "utilisée pour votre candidature ?"
    ),
    "campus": (
        "Dans quel campus votre test est-il "
        "prévu : Safi, Youssoufia ou Nador ?"
    ),
    "scheduled_test_date": (
        "Quelle est la date actuelle de "
        "votre test ?"
    ),
    "requested_test_date": (
        "À partir de quelle date "
        "souhaitez-vous passer le test ?"
    ),
    "description": (
        "Pouvez-vous décrire brièvement "
        "la raison de votre demande ?"
    ),
}


class SupportNodes:
    def __init__(
        self,
        *,
        extractor: (
            SupportExtractor | None
        ) = None,
    ) -> None:
        self.extractor = (
            extractor
            or create_support_extractor()
        )

    def extract_information(
        self,
        state: YouCodeState,
    ) -> dict:
        """
        Utilise le LLM pour extraire les
        informations du dernier message.
        """

        message = self._get_last_user_message(
            state
        )

        current_draft: SupportDraft = dict(
            state.get(
                "support_draft",
                {},
            )
        )

        extraction = (
            self.extractor
            .extract_information(
                message=message,
                current_draft=(
                    current_draft
                ),
            )
        )

        extracted_values = (
            extraction.model_dump(
                exclude_none=True,
                mode="json",
            )
        )

        updated_draft: SupportDraft = {
            **current_draft,
            **extracted_values,
        }

        ambiguities = list(
            updated_draft.get(
                "ambiguities",
                [],
            )
        )

        email = updated_draft.get(
            "email"
        )

        if email and not self._is_valid_email(
            email
        ):
            updated_draft.pop(
                "email",
                None,
            )

            ambiguities.append(
                "L’adresse e-mail fournie "
                "n’est pas valide."
            )

        scheduled_date = (
            updated_draft.get(
                "scheduled_test_date"
            )
        )

        requested_date = (
            updated_draft.get(
                "requested_test_date"
            )
        )

        if (
            scheduled_date
            and requested_date
        ):
            scheduled_date = (
                date.fromisoformat(
                    scheduled_date
                )
            )

            requested_date = (
                date.fromisoformat(
                    requested_date
                )
            )

            if requested_date <= scheduled_date:
                updated_draft.pop(
                    "requested_test_date",
                    None,
                )

                ambiguities.append(
                    "La nouvelle date doit être "
                    "postérieure à la date "
                    "actuelle du test."
                )   


        updated_draft[
            "ambiguities"
        ] = ambiguities

        return {
            "active_agent": "support",
            "support_phase": "collecting",
            "support_draft": (
                updated_draft
            ),
            "consent_confirmed": False,
            "final_response": None,
            "requires_human": False,
        }

    def request_missing_information(
        self,
        state: YouCodeState,
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

        missing_fields = (
            self._get_missing_fields(
                draft
            )
        )

        if missing_fields:
            field_name = missing_fields[0]

            answer = QUESTION_BY_FIELD[
                field_name
            ]

            return self._answer_update(
                state=state,
                status="collecting",
                answer=answer,
                support_phase="collecting",
            )

        answer = self._create_consent_message(
            draft
        )

        return self._answer_update(
            state=state,
            status="awaiting_consent",
            answer=answer,
            support_phase=(
                "awaiting_consent"
            ),
        )

    def classify_consent(
        self,
        state: YouCodeState,
    ) -> dict:
        """
        Analyse le dernier message uniquement
        lorsque le consentement a été demandé.
        """

        message = self._get_last_user_message(
            state
        )

        extraction = (
            self.extractor
            .extract_consent(
                message=message
            )
        )

        if (
            extraction.decision
            == "accepted"
        ):
            return {
                "active_agent": "support",
                "support_phase": "processing",
                "consent_confirmed": True,
                "final_response": None,
                "requires_human": False,
            }

        if (
            extraction.decision
            == "refused"
        ):
            answer = (
                "Votre demande n’a pas été "
                "enregistrée."
            )

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
            support_phase=(
                "awaiting_consent"
            ),
        )

    def process_request(
        self,
        state: YouCodeState,
    ) -> dict:
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
                "Le consentement est nécessaire "
                "avant l’enregistrement de la "
                "demande."
            )

            return self._answer_update(
                state=state,
                status="awaiting_consent",
                answer=answer,
                support_phase=(
                    "awaiting_consent"
                ),
            )

        draft = state.get(
            "support_draft",
            {},
        )

        try:
            request_data = (
                SupportRequestCreate(
                    session_id=state[
                        "session_id"
                    ],
                    request_type=draft[
                        "request_type"
                    ],
                    email=draft["email"],
                    language=draft.get(
                        "language",
                        Language.FR.value,
                    ),
                    campus=draft.get(
                        "campus"
                    ),
                    description=draft[
                        "description"
                    ],
                    scheduled_test_date=(
                        draft.get(
                            "scheduled_test_date"
                        )
                    ),
                    requested_test_date=(
                        draft.get(
                            "requested_test_date"
                        )
                    ),
                )
            )

            with database_session() as session:
                support_service = (
                    create_support_request_service(
                        session=session
                    )
                )

                created_request = (
                    support_service
                    .create_request(
                        request_data
                    )
                )

                if (
                    request_data.request_type
                    == RequestType
                    .TEST_RESCHEDULE.value
                ):
                    rescheduling_service = (
                        create_rescheduling_service(
                            session=session
                        )
                    )

                    proposal = (
                        rescheduling_service
                        .process(
                            reference=(
                                created_request
                                .reference
                            ),
                            session_id=state[
                                "session_id"
                            ],
                        )
                    )

                    proposed_date = (
                        proposal.proposed_test_date
                    )

                    formatted_date = (
                        proposed_date.strftime(
                            "%d/%m/%Y à %H:%M"
                        )
                    )

                    answer = (
                        "Votre demande a été enregistrée "
                        f"avec la référence "
                        f"{proposal.reference}. "
                        "La prochaine session disponible "
                        f"est prévue le {formatted_date}. "
                        "Cette date vous convient-elle ? "
                        "Répondez par oui ou non. "
                        "Si elle ne vous convient pas, "
                        "je rechercherai une autre session."
                    )

                    return self._answer_update(
                        state=state,
                        status=(
                            "awaiting_session_confirmation"
                        ),
                        answer=answer,
                        support_phase=(
                            "awaiting_session_confirmation"
                        ),
                        active_agent="support",
                        request_reference=(
                            proposal.reference
                        ),
                        proposed_session_id=(
                            proposal.external_session_id
                        ),
                        proposed_test_date=(
                            proposed_date.isoformat()
                        ),
                        requires_human=False,
                    )

                answer = (
                    "Votre demande a été "
                    "enregistrée avec la référence "
                    f"{created_request.reference}. "
                    "Elle sera transmise à un "
                    "responsable."
                )

                return self._answer_update(
                    state=state,
                    status=(
                        "requires_human"
                    ),
                    answer=answer,
                    support_phase="completed",
                    active_agent=None,
                    request_reference=(
                        created_request.reference
                    ),
                    requires_human=True
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
        state: YouCodeState,
    ) -> dict:
        message = self._get_last_user_message(
            state
        )

        decision = (
            self.extractor
            .extract_session_decision(
                message=message,
                proposed_test_date=state[
                    "proposed_test_date"
                ],
            )
        )

        if decision.decision == "accepted":
            return {
                "support_phase": (
                    "confirming_session"
                ),
            }

        if decision.decision == "refused":
            rejected_ids = list(
                state.get(
                    "rejected_session_ids",
                    [],
                )
            )

            current_session_id = state.get(
                "proposed_session_id"
            )

            if (
                current_session_id
                and current_session_id
                not in rejected_ids
            ):
                rejected_ids.append(
                    current_session_id
                )

            return {
                "support_phase": (
                    "searching_alternative"
                ),
                "rejected_session_ids": (
                    rejected_ids
                ),
            }

        answer = (
            "Cette date vous convient-elle ? "
            "Répondez par oui ou non."
        )

        return self._answer_update(
            state=state,
            status=(
                "awaiting_session_confirmation"
            ),
            answer=answer,
            support_phase=(
                "awaiting_session_confirmation"
            ),
        )


    def confirm_session_proposal(
        self,
        state: YouCodeState,
    ) -> dict:
        with database_session() as session:
            service = (
                create_rescheduling_service(
                    session=session
                )
            )

            result = service.confirm_proposal(
                reference=state[
                    "request_reference"
                ],
                session_id=state[
                    "session_id"
                ],
            )

        proposed_date = (
            result.proposed_test_date
            .strftime("%d/%m/%Y à %H:%M")
        )

        answer = (
            f"La date du {proposed_date} a été "
            "acceptée. Votre demande attend "
            "maintenant une validation humaine. "
            f"Référence : {result.reference}."
        )

        return self._answer_update(
            state=state,
            status="proposed",
            answer=answer,
            support_phase="completed",
            active_agent=None,
            request_reference=(
                result.reference
            ),
            proposed_test_date=(
                result.proposed_test_date
                .isoformat()
            ),
            requires_human=True,
        )


    def search_alternative_session(
        self,
        state: YouCodeState,
    ) -> dict:
        with database_session() as session:
            service = (
                create_rescheduling_service(
                    session=session
                )
            )

            result = service.propose_alternative(
                reference=state[
                    "request_reference"
                ],
                session_id=state[
                    "session_id"
                ],
                excluded_session_ids=set(
                    state.get(
                        "rejected_session_ids",
                        [],
                    )
                ),
            )

        proposed_date = (
            result.proposed_test_date
            .strftime("%d/%m/%Y à %H:%M")
        )

        answer = (
            "Une autre session est disponible "
            f"le {proposed_date}. "
            "Cette nouvelle date vous "
            "convient-elle ? Répondez par "
            "oui ou non."
        )

        return self._answer_update(
            state=state,
            status=(
                "awaiting_session_confirmation"
            ),
            answer=answer,
            support_phase=(
                "awaiting_session_confirmation"
            ),
            active_agent="support",
            request_reference=(
                result.reference
            ),
            proposed_session_id=(
                result.external_session_id
            ),
            proposed_test_date=(
                result.proposed_test_date
                .isoformat()
            ),
            requires_human=False,
        )

    

    @staticmethod
    def _get_missing_fields(
        draft: SupportDraft,
    ) -> list[str]:
        missing_fields: list[str] = []

        request_type = draft.get(
            "request_type"
        )

        if request_type is None:
            missing_fields.append(
                "request_type"
            )

        if not draft.get("email"):
            missing_fields.append(
                "email"
            )

        if (
            request_type
            == RequestType.TEST_RESCHEDULE.value
        ):
            if not draft.get("campus"):
                missing_fields.append(
                    "campus"
                )

            if not draft.get(
                "scheduled_test_date"
            ):
                missing_fields.append(
                    "scheduled_test_date"
                )

            if not draft.get(
                "requested_test_date"
            ):
                missing_fields.append(
                    "requested_test_date"
                )

        if not draft.get("description"):
            missing_fields.append(
                "description"
            )

        return missing_fields

    @staticmethod
    def _get_last_user_message(
        state: YouCodeState,
    ) -> str:
        for message in reversed(
            state.get("messages", [])
        ):
            if isinstance(
                message,
                HumanMessage,
            ):
                return str(
                    message.content
                ).strip()

        raise ValueError(
            "No user message was found."
        )

    @staticmethod
    def _is_valid_email(
        email: str,
    ) -> bool:
        try:
            EMAIL_ADAPTER.validate_python(
                email
            )
        except ValidationError:
            return False

        return True

    @staticmethod
    def _create_consent_message(
        draft: SupportDraft,
    ) -> str:
        request_type = draft.get(
            "request_type"
        )

        email = draft.get("email")

        if (
            request_type
            == RequestType.TEST_RESCHEDULE.value
        ):
            campus = draft.get(
                "campus"
            )

            scheduled_date = date.fromisoformat(draft.get(
                "scheduled_test_date"
            ))

            requested_date = date.fromisoformat(draft.get(
                "requested_test_date"
            ))

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
        state: YouCodeState,
        status: str,
        answer: str,
        support_phase: str,
        active_agent: str | None = (
            "support"
        ),
        request_reference: (
            str | None
        ) = None,
        requires_human: bool = False,
        proposed_test_date: (
            str | None
        ) = None,
        proposed_session_id: (
            str | None
        ) = None,
    ) -> dict:
        language = (
            state.get(
                "support_draft",
                {},
            ).get(
                "language",
                Language.FR,
            )
        )

        response = SupportWorkflowResponse(
            status=status,
            language=language,
            answer=answer,
            request_reference=(
                request_reference
            ),
            requires_human=(
                requires_human
            ),
            proposed_test_date=(
                proposed_test_date
            ),
        )

        return {
            "messages": [
                AIMessage(
                    content=answer
                )
            ],
            "active_agent": active_agent,
            "support_phase": support_phase,
            "request_reference": (
                request_reference
            ),
            "final_response": (
                response.model_dump(
                    mode="json"
                )
            ),
            "requires_human": (
                requires_human
            ),
            "proposed_test_date": (
                proposed_test_date
            ),
            "proposed_session_id": (
                proposed_session_id
            ),
            "rejected_session_ids": (
                state.get(
                    "rejected_session_ids",
                    [],
                )
            ),
        }



def create_support_nodes():
    return SupportNodes()