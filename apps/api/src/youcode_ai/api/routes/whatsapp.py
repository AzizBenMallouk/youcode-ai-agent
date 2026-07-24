from functools import lru_cache

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from pydantic import BaseModel
from youcode_ai.orchestration.service import (
    YouCodeOrchestrationService,
)

router = APIRouter(
    prefix="/whatsapp",
    tags=["WhatsApp"],
)


class WhatsAppProcessRequest(BaseModel):
    session_id: str
    message: str


class WhatsAppProcessResponse(BaseModel):
    answer: str
    status: str


@lru_cache(maxsize=1)
def get_orchestration_service() -> YouCodeOrchestrationService:
    return YouCodeOrchestrationService()


@router.post(
    "/process",
    response_model=WhatsAppProcessResponse,
)
def process_whatsapp_message(
    payload: WhatsAppProcessRequest,
    service: YouCodeOrchestrationService = Depends(get_orchestration_service),
) -> WhatsAppProcessResponse:
    """
    Reçoit un message depuis le script Node.js (whatsapp-web.js),
    l'envoie à l'Orchestrateur IA, et retourne la réponse.
    """
    try:
        # On passe le message à LangGraph
        result = service.invoke(
            session_id=payload.session_id,
            message=payload.message,
        )

        # On extrait la réponse générée par l'IA
        answer = str(result.get("answer", "Désolé, je n'ai pas pu générer de réponse."))
        msg_status = str(result.get("status", "answered"))

        return WhatsAppProcessResponse(
            answer=answer,
            status=msg_status,
        )

    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to process the message.",
        ) from error
