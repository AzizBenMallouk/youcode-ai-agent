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
from fastapi.responses import HTMLResponse

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration — read from env directly (no heavy shared Settings class)
# ---------------------------------------------------------------------------
ORCHESTRATOR_URL: str = os.getenv("ORCHESTRATOR_URL", "http://orchestrator:8006")
EVOLUTION_API_URL: str = os.getenv("EVOLUTION_API_URL", "http://evolution-api:8080")
EVOLUTION_API_KEY: str = os.getenv("EVOLUTION_API_KEY", "B6D711FCDE4D4FD5936544120E713976")
WEBHOOK_SECRET: str = os.getenv("WEBHOOK_SECRET", "")
ALLOWED_WHATSAPP_NUMBERS_STR: str = os.getenv("ALLOWED_WHATSAPP_NUMBERS", "")
ALLOWED_WHATSAPP_NUMBERS = [n.strip() for n in ALLOWED_WHATSAPP_NUMBERS_STR.split(",") if n.strip()]

# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------
app = FastAPI(title="YouCode AI — Gateway Service")

@app.get("/qr", response_class=HTMLResponse)
async def qr_interface():
    """Minimal interface to see and scan the WhatsApp QR Code."""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>YouCode AI - WhatsApp QR</title>
        <style>
            body { font-family: -apple-system, sans-serif; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; background: #f3f4f6; margin: 0; }
            .card { background: white; padding: 2rem; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; max-width: 400px; }
            h1 { color: #111827; font-size: 1.5rem; margin-top: 0; }
            p { color: #4b5563; font-size: 0.9rem; }
            #qr-container { margin: 1.5rem 0; min-height: 256px; display: flex; align-items: center; justify-content: center; }
            img { max-width: 256px; border-radius: 8px; }
            button { background: #2563eb; color: white; border: none; padding: 0.75rem 1.5rem; border-radius: 6px; cursor: pointer; font-weight: 500; transition: background 0.2s; }
            button:hover { background: #1d4ed8; }
            .error { color: #ef4444; font-size: 0.85rem; margin-top: 1rem; }
        </style>
    </head>
    <body>
        <div class="card">
            <h1>Connexion WhatsApp</h1>
            <p>Scannez ce QR Code avec votre application WhatsApp pour connecter le Bot YouCode AI.</p>
            <div id="qr-container">
                <span id="loading" style="color: #6b7280;">Chargement du QR Code...</span>
            </div>
            <button onclick="fetchQR()">Rafraîchir le QR Code</button>
            <div id="error" class="error"></div>
        </div>

        <script>
            async function fetchQR() {
                const container = document.getElementById('qr-container');
                const errorDiv = document.getElementById('error');
                
                try {
                    errorDiv.innerText = '';
                    const response = await fetch('/api/v1/qr/youcode-ai');
                    const data = await response.json();
                    
                    if (data.status === 'connected') {
                        container.innerHTML = '<span style="color: #10b981; font-weight: bold;">WhatsApp est déjà connecté ! ✅</span>';
                    } else if (data.base64) {
                        container.innerHTML = `<img src="${data.base64}" alt="QR Code" />`;
                    } else {
                        throw new Error("QR Code introuvable dans la réponse.");
                    }
                } catch (err) {
                    errorDiv.innerText = "Erreur lors de la récupération du QR Code: " + err.message;
                    container.innerHTML = '<span style="color: #ef4444;">Erreur</span>';
                }
            }
            // Fetch on load
            fetchQR();
            // Refresh every 15 seconds automatically
            setInterval(fetchQR, 15000);
        </script>
    </body>
    </html>
    """

@app.get("/api/v1/qr/{instance_name}")
async def get_qr_code(instance_name: str) -> dict:
    """Proxy request to fetch base64 QR code from Evolution API."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                f"{EVOLUTION_API_URL}/instance/connect/{instance_name}",
                headers={"apikey": EVOLUTION_API_KEY}
            )
            # If 403 or 401, check the instance state. It might be already connected.
            if resp.status_code != 200:
                # Try to get connection state
                state_resp = await client.get(
                    f"{EVOLUTION_API_URL}/instance/connectionState/{instance_name}",
                    headers={"apikey": EVOLUTION_API_KEY}
                )
                if state_resp.status_code == 200 and state_resp.json().get("instance", {}).get("state") == "open":
                    return {"status": "connected"}
                
                return {"status": "error", "message": f"Evolution API returned {resp.status_code}"}

            return resp.json()
    except Exception as exc:
        logger.error("Error fetching QR: %s", exc)
        return {"status": "error", "message": str(exc)}


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


@app.post("/api/v1/webhook/whatsapp")
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
        
        if not remote_jid or not instance:
            return {"status": "ignored", "reason": "missing data"}

        # Whitelist check: only process requests from allowed numbers
        if ALLOWED_WHATSAPP_NUMBERS:
            number_only = remote_jid.split("@")[0]
            # Match if the allowed number is part of the remote_jid (e.g. allowing without country code)
            if not any(allowed in number_only for allowed in ALLOWED_WHATSAPP_NUMBERS):
                logger.info("Ignored message from unauthorized number: %s", remote_jid)
                return {"status": "ignored", "reason": "unauthorized number"}

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
