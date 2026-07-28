"""Gateway Service — WhatsApp webhook receiver and proxy.

Receives events from Evolution API (WhatsApp), filters relevant
messages, and proxies them to the Orchestrator for AI processing.

This service is intentionally lightweight — no LLM, no database.
It reads its configuration from environment variables directly.
"""

import logging
import os

import httpx
from fastapi import BackgroundTasks, FastAPI, Request

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration — read from env directly (no heavy shared Settings class)
# ---------------------------------------------------------------------------
ORCHESTRATOR_URL: str = os.getenv("ORCHESTRATOR_URL", "http://orchestrator:8010")
EVOLUTION_API_URL: str = os.getenv("EVOLUTION_API_URL", "http://evolution-api:8080")
EVOLUTION_API_KEY: str = os.getenv("EVOLUTION_API_KEY", "super_secret_key")
WEBHOOK_SECRET: str = os.getenv("WEBHOOK_SECRET", "")

# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------
app = FastAPI(title="YouCode AI — Gateway Service")


async def process_and_reply(instance: str, remote_jid: str, message_text: str) -> None:
    """Background task: forward message to Orchestrator, send reply via Evolution API."""
    try:
        # 1. Send to Orchestrator
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                f"{ORCHESTRATOR_URL}/api/v1/invoke",
                json={"user_id": remote_jid, "message": message_text},
            )
            resp.raise_for_status()
            result = resp.json()
            answer: str = result.get("response", "Désolé, je n'ai pas pu générer de réponse.")

        # 2. Send reply via Evolution API
        response_url = f"{EVOLUTION_API_URL}/message/sendText/{instance}"
        payload = {
            "number": remote_jid,
            "options": {"delay": 1000, "presence": "composing"},
            "text": answer,
        }
        headers = {"apikey": EVOLUTION_API_KEY, "Content-Type": "application/json"}

        async with httpx.AsyncClient(timeout=30.0) as client:
            await client.post(response_url, json=payload, headers=headers)

    except Exception as exc:
        logger.error("Error processing message for %s: %s", remote_jid, exc)


@app.post("/api/v1/whatsapp/webhook")
async def whatsapp_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
) -> dict:
    """Receive Evolution API webhooks and dispatch messages for processing."""
    try:
        payload = await request.json()

        # Only process messages.upsert events
        if payload.get("event") != "messages.upsert":
            return {"status": "ignored", "reason": "not messages.upsert"}

        data = payload.get("data", {})
        key = data.get("key", {})

        # Ignore messages sent by us
        if key.get("fromMe") is True:
            return {"status": "ignored", "reason": "fromMe"}

        remote_jid: str | None = key.get("remoteJid")
        instance: str | None = payload.get("instance")

        message_obj: dict = data.get("message", {})
        message_text: str | None = message_obj.get("conversation")
        if not message_text and "extendedTextMessage" in message_obj:
            message_text = message_obj["extendedTextMessage"].get("text")

        if not remote_jid or not message_text or not instance:
            return {"status": "ignored", "reason": "missing data"}

        background_tasks.add_task(process_and_reply, instance, remote_jid, message_text)
        return {"status": "accepted"}

    except Exception as exc:
        logger.error("Webhook processing error: %s", exc)
        return {"status": "error"}


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "healthy", "service": "gateway", "version": "2.0.0"}
