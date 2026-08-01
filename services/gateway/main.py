"""Gateway Service — WhatsApp webhook receiver and proxy.

Receives events from Evolution API (WhatsApp), filters relevant
messages, and publishes them to RabbitMQ for Orchestrator processing.

This service is intentionally lightweight — no LLM, no database.
It reads its configuration from environment variables directly.
"""

import json
import logging
import os
from contextlib import asynccontextmanager

import aio_pika
import httpx
from fastapi import BackgroundTasks, FastAPI, Request
from fastapi.responses import HTMLResponse

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration — read from env directly
# ---------------------------------------------------------------------------
RABBITMQ_URL: str = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")
EVOLUTION_API_URL: str = os.getenv("EVOLUTION_API_URL", "http://evolution-api:8080")
EVOLUTION_API_KEY: str = os.getenv("EVOLUTION_API_KEY", "B6D711FCDE4D4FD5936544120E713976")
WEBHOOK_SECRET: str = os.getenv("WEBHOOK_SECRET", "")
ALLOWED_WHATSAPP_NUMBERS_STR: str = os.getenv("ALLOWED_WHATSAPP_NUMBERS", "")
ALLOWED_WHATSAPP_NUMBERS = [n.strip() for n in ALLOWED_WHATSAPP_NUMBERS_STR.split(",") if n.strip()]


# ---------------------------------------------------------------------------
# RabbitMQ Connection Management
# ---------------------------------------------------------------------------
class RabbitMQClient:
    connection: aio_pika.RobustConnection | None = None
    channel: aio_pika.RobustChannel | None = None
    exchange: aio_pika.RobustExchange | None = None

mq = RabbitMQClient()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Connect to RabbitMQ
    logger.info("Connecting to RabbitMQ...")
    try:
        mq.connection = await aio_pika.connect_robust(RABBITMQ_URL)
        mq.channel = await mq.connection.channel()
        # Declare queue to ensure it exists with DLQ arguments to avoid conflict with Orchestrator
        await mq.channel.declare_queue("whatsapp_messages_dlq", durable=True)
        await mq.channel.declare_queue(
            "whatsapp_messages", 
            durable=True,
            arguments={
                "x-dead-letter-exchange": "",
                "x-dead-letter-routing-key": "whatsapp_messages_dlq"
            }
        )
        
        # Start consuming outbound messages from Orchestrator
        await start_outbound_consumer()
        
        logger.info("RabbitMQ connected successfully.")
    except Exception as e:
        logger.error("Failed to connect to RabbitMQ: %s", e)
    
    yield
    
    # Cleanup
    if mq.connection:
        await mq.connection.close()

# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------
app = FastAPI(title="YouCode AI — Gateway Service", lifespan=lifespan)

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
            fetchQR();
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
            if resp.status_code != 200:
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

async def publish_message(instance: str, remote_jid: str, message_text: str) -> None:
    """Publish the incoming message to RabbitMQ."""
    if not mq.channel:
        logger.error("RabbitMQ channel not available")
        return
        
    try:
        payload = {
            "instance": instance,
            "user_id": remote_jid,
            "message": message_text
        }
        message = aio_pika.Message(
            body=json.dumps(payload).encode(),
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT
        )
        await mq.channel.default_exchange.publish(
            message,
            routing_key="whatsapp_messages"
        )
        logger.info("Published message from %s to RabbitMQ", remote_jid)
    except Exception as exc:
        logger.error("Error publishing message for %s: %s", remote_jid, exc)

async def send_whatsapp_message(payload: dict) -> None:
    """Send text message to WhatsApp via Evolution API."""
    instance = payload.get("instance")
    user_id = payload.get("user_id")
    answer = payload.get("text")
    
    if not instance or not user_id or not answer:
        logger.error("Invalid payload for outbound message: %s", payload)
        return

    response_url = f"{EVOLUTION_API_URL}/message/sendText/{instance}"
    evo_payload = {
        "number": user_id,
        "options": {"delay": 1000, "presence": "composing"},
        "text": answer,
    }
    headers = {
        "apikey": EVOLUTION_API_KEY,
        "Content-Type": "application/json",
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                response_url, json=evo_payload, headers=headers
            )
            if resp.status_code >= 400:
                logger.warning(
                    "Evolution API returned %d for %s",
                    resp.status_code,
                    user_id,
                )
    except Exception as exc:
        logger.error("Failed to send reply via Evolution API: %s", exc)

async def start_outbound_consumer() -> None:
    """Consume outbound messages from RabbitMQ and send them to WhatsApp."""
    if not mq.channel:
        return
    queue = await mq.channel.declare_queue("whatsapp_outbound", durable=True)
    
    async def on_outbound_message(message: aio_pika.abc.AbstractIncomingMessage) -> None:
        async with message.process():
            try:
                payload = json.loads(message.body.decode())
                await send_whatsapp_message(payload)
            except Exception as exc:
                logger.error("Error processing outbound message: %s", exc)
                
    await queue.consume(on_outbound_message)
    logger.info("Gateway started consuming 'whatsapp_outbound' queue.")

@app.post("/api/v1/webhook/whatsapp")
async def whatsapp_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
) -> dict:
    """Receive Evolution API webhooks and dispatch messages for processing."""
    
    # 1. Webhook Security: Verify Secret
    if WEBHOOK_SECRET:
        # Evolution API can send the secret in various ways depending on config
        # We check both Authorization header and custom x-webhook-secret header
        auth_header = request.headers.get("Authorization", "")
        secret_header = request.headers.get("x-webhook-secret", "")
        
        token = auth_header.replace("Bearer ", "").strip() if "Bearer" in auth_header else auth_header
        
        if token != WEBHOOK_SECRET and secret_header != WEBHOOK_SECRET:
            logger.warning("Webhook blocked: Invalid or missing WEBHOOK_SECRET.")
            # We return a generic 403-like JSON instead of raising HTTPError to not break Evolution retries abruptly
            return {"status": "ignored", "reason": "unauthorized signature"}

    try:
        payload = await request.json()

        if payload.get("event") != "messages.upsert":
            return {"status": "ignored", "reason": "not messages.upsert"}

        data = payload.get("data", {})
        key = data.get("key", {})

        if key.get("fromMe") is True:
            return {"status": "ignored", "reason": "fromMe"}

        remote_jid: str | None = key.get("remoteJid")
        instance: str | None = payload.get("instance")
        
        if not remote_jid or not instance:
            return {"status": "ignored", "reason": "missing data"}

        if ALLOWED_WHATSAPP_NUMBERS:
            number_only = remote_jid.split("@")[0]
            if not any(allowed in number_only for allowed in ALLOWED_WHATSAPP_NUMBERS):
                return {"status": "ignored", "reason": "unauthorized number"}

        message_obj: dict = data.get("message", {})
        message_text: str | None = message_obj.get("conversation")
        if not message_text and "extendedTextMessage" in message_obj:
            message_text = message_obj["extendedTextMessage"].get("text")

        if not remote_jid or not message_text or not instance:
            return {"status": "ignored", "reason": "missing data"}

        background_tasks.add_task(publish_message, instance, remote_jid, message_text)
        return {"status": "accepted"}

    except Exception as exc:
        logger.error("Webhook processing error: %s", exc)
        return {"status": "error"}

@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "healthy", "service": "gateway", "version": "2.0.0", "queue_connected": str(mq.channel is not None)}
