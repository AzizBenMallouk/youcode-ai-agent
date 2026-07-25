import os
from functools import lru_cache
from typing import Dict, Any
import httpx

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    BackgroundTasks,
    Request
)
from pydantic import BaseModel
from youcode_ai.orchestration.service import (
    YouCodeOrchestrationService,
)

router = APIRouter(
    prefix="/whatsapp",
    tags=["WhatsApp"],
)


@lru_cache(maxsize=1)
def get_orchestration_service() -> YouCodeOrchestrationService:
    return YouCodeOrchestrationService()


def process_and_reply(
    instance: str,
    remote_jid: str,
    message_text: str,
    service: YouCodeOrchestrationService
):
    """
    Tâche asynchrone qui traite le message via LangGraph 
    et renvoie la réponse à Evolution API.
    """
    try:
        # 1. Traitement par l'IA
        result = service.invoke(
            session_id=remote_jid,
            message=message_text,
        )
        answer = str(result.get("answer", "Désolé, je n'ai pas pu générer de réponse."))

        # 2. Envoi de la réponse via Evolution API
        evolution_url = os.environ.get("EVOLUTION_API_URL", "http://evolution-api:8080")
        api_key = os.environ.get("EVOLUTION_API_KEY", "super_secret_key")

        headers = {
            "apikey": api_key,
            "Content-Type": "application/json"
        }
        payload = {
            "number": remote_jid,
            "options": {
                "delay": 1000,
                "presence": "composing"
            },
            "textMessage": {
                "text": answer
            }
        }

        response_url = f"{evolution_url}/message/sendText/{instance}"
        with httpx.Client(timeout=30.0) as client:
            client.post(response_url, json=payload, headers=headers)

    except Exception as e:
        print(f"Error processing Evolution Webhook for {remote_jid}: {e}")


@router.post("/webhook")
async def evolution_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    service: YouCodeOrchestrationService = Depends(get_orchestration_service)
):
    """
    Reçoit les webhooks d'Evolution API (messages.upsert),
    acquitte immédiatement (200 OK) et traite en arrière-plan.
    """
    try:
        payload = await request.json()

        # On ne traite que l'événement "messages.upsert"
        if payload.get("event") != "messages.upsert":
            return {"status": "ignored", "reason": "not messages.upsert"}

        data = payload.get("data", {})
        key = data.get("key", {})
        
        # Ignorer les messages envoyés par nous-mêmes
        if key.get("fromMe") is True:
            return {"status": "ignored", "reason": "fromMe"}

        remote_jid = key.get("remoteJid")
        instance = payload.get("instance")
        
        message_obj = data.get("message", {})
        # Evolution API formatte le texte soit dans conversation, soit dans extendedTextMessage
        message_text = message_obj.get("conversation")
        if not message_text and "extendedTextMessage" in message_obj:
            message_text = message_obj["extendedTextMessage"].get("text")

        if not remote_jid or not message_text or not instance:
            return {"status": "ignored", "reason": "missing data"}

        # Ajouter le traitement en arrière-plan
        background_tasks.add_task(
            process_and_reply,
            instance,
            remote_jid,
            message_text,
            service
        )

        return {"status": "accepted"}

    except Exception as error:
        print(f"Webhook processing error: {error}")
        # Toujours retourner 200 pour qu'Evolution API ne retente pas en boucle
        return {"status": "error"}
