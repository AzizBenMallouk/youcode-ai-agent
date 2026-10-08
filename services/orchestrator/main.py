"""Orchestrator Service — RabbitMQ RPC Client.

Receives messages from RabbitMQ (whatsapp_messages and incoming_messages queues),
runs the Supervisor/Guardrail LangGraph to determine the correct agent,
then delegates to the agent via RabbitMQ RPC.

When an agent returns requires_human=True, notifies the admin via Email MCP.
Publishes responses to outbound_messages (with source field) and
whatsapp_outbound (legacy) queues.
"""

import asyncio
import json
import logging
import os
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, Request
from langchain_core.messages import HumanMessage

from shared.core.config import settings
from shared.infrastructure.database.checkpointer import create_checkpointer
from shared.messaging import MessageBroker, RPCClient
from shared.messaging.resilience import resilient_rpc_call

from .graph import create_graph
from .schemas import IncomingMessage, OutgoingResponse

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

RABBITMQ_URL: str = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")

# Map route names to RabbitMQ queue names
_AGENT_QUEUES: dict[str, str] = {
    "guide": "guide_requests",
    "support": "support_requests",
    "newsletter": "newsletter_requests",
    "admin": "admin_requests",
}


async def _notify_admin_requires_human(
    user_id: str,
    route: str,
    summary: str,
) -> None:
    """
    Call the Email MCP to notify the admin when requires_human=True.
    Runs fire-and-forget — never blocks the response to the user.
    """
    try:
        subject = f"[YouCode AI] Intervention requise — Agent {route.capitalize()}"
        body = (
            f"Un ticket nécessite une intervention humaine.\n\n"
            f"Utilisateur : {user_id}\n"
            f"Agent : {route}\n"
            f"Résumé : {summary[:500]}"
        )
        async with httpx.AsyncClient(timeout=10.0) as client:
            await client.post(
                f"{settings.email_mcp_url}/mcp",
                json={
                    "tool": "send_admin_notification",
                    "arguments": {
                        "subject": subject,
                        "body": body,
                        "admin_email": settings.admin_email,
                    },
                },
            )
        logger.info("Admin notification sent for user %s (agent: %s).", user_id, route)
    except Exception as exc:
        # Non-blocking — log and continue
        logger.warning("Failed to send admin notification: %s", exc)


async def process_whatsapp_message(
    payload: dict,
    graph,
    rpc_client: RPCClient,
) -> None:
    """Traite un message WhatsApp reçu de RabbitMQ."""
    instance = payload.get("instance")
    user_id = payload.get("user_id")
    text = payload.get("message")

    logger.info("Processing message for %s", user_id)

    try:
        # Mock staff detection
        staff_phones = ["212600000000", "212600000001", "test_admin"]
        is_staff = any(user_id.startswith(phone) for phone in staff_phones) or "staff" in user_id.lower()
        role = "admin" if user_id.startswith("212600000000") else "formateur"
        
        route = "admin" if is_staff else None
        orch_result = {}

        if not is_staff:
            # 1. Run Supervisor/Guardrail graph
            thread_id = f"orch_{user_id}"
            config = {"configurable": {"thread_id": thread_id}}
            state_update = {
                "messages": [HumanMessage(content=text)],
                "session_id": thread_id,
                "user_id": user_id,
            }

            orch_result = await graph.ainvoke(state_update, config)
            route = orch_result.get("route", "clarification")

        # Initialize result to avoid UnboundLocalError
        result = {}

        # 2. Check if it's a direct response (guardrail refusal, clarification)
        target_queue = _AGENT_QUEUES.get(route)
        if not target_queue or orch_result.get("active_agent") == "guardrail_refusal":
            messages = orch_result.get("messages", [])
            if messages:
                answer = messages[-1].content
            else:
                final_resp = orch_result.get("final_response", {})
                answer = final_resp.get(
                    "answer", "Je ne peux pas répondre à cette demande."
                )
        else:
            # 3. Delegate to agent via RabbitMQ RPC
            try:
                result = await resilient_rpc_call(
                    rpc_client,
                    target_queue,
                    {"user_id": user_id, "message": text, "role": role if is_staff else "user"},
                    timeout=120.0,
                )
                answer = result.get("response", "Aucune réponse de l'agent.")

                if result.get("error"):
                    logger.warning(
                        "Agent %s returned error: %s",
                        route,
                        result["error"],
                    )
            except TimeoutError:
                logger.error("RPC timeout calling %s for user %s", route, user_id)
                answer = "Le traitement prend plus de temps que prévu. Veuillez réessayer."
            except Exception as exc:
                logger.error("RPC call to %s failed: %s", route, exc)
                answer = f"Le service {route} est temporairement indisponible."

        if result.get("requires_human"):
                asyncio.create_task(
                    _notify_admin_requires_human(
                        user_id=user_id,
                        route=route or "unknown",
                        summary=answer,
                    )
                )

        # 4. Publish reply to Gateway (whatsapp_outbound queue)
        # logger.info("Generated answer for %s: %s", user_id, answer[:100])
        logger.info("Generated answer for %s: %s", user_id, answer)
        try:
            broker = rpc_client._broker
            # Publish to shared multi-source outbound queue (with source field)
            source = payload.get("source", "whatsapp")
            await broker.publish(
                "outbound_messages",
                {
                    "source": source,
                    "instance": instance,
                    "user_id": user_id,
                    "text": answer,
                },
            )
            # Also publish to legacy whatsapp_outbound for backward compat
            if source == "whatsapp":
                await broker.publish(
                    "whatsapp_outbound",
                    {
                        "instance": instance,
                        "user_id": user_id,
                        "text": answer,
                    },
                )
        except Exception as exc:
            logger.error("Failed to publish reply: %s", exc)

        logger.info("Successfully processed message for %s", user_id)

    except Exception:
        logger.exception("Error processing message for %s", user_id)


async def start_whatsapp_consumer(
    broker: MessageBroker,
    graph,
    rpc_client: RPCClient,
) -> None:
    """Consume from both whatsapp_messages (legacy) and incoming_messages (multi-source)."""
    await broker.set_qos(prefetch_count=10)

    async def on_message(message) -> None:
        async with message.process():
            try:
                payload = json.loads(message.body.decode())
            except (json.JSONDecodeError, UnicodeDecodeError) as exc:
                logger.error("Invalid message body: %s", exc)
                return
            asyncio.create_task(
                process_whatsapp_message(payload, graph, rpc_client)
            )

    # Legacy queue
    legacy_queue = await broker.declare_queue(
        "whatsapp_messages", durable=True, with_dlq=True
    )
    await legacy_queue.consume(on_message)

    # Shared multi-source queue (Discord, WhatsApp, future sources)
    shared_queue = await broker.declare_queue(
        "incoming_messages", durable=True, with_dlq=False
    )
    await shared_queue.consume(on_message)

    logger.info("Orchestrator consuming 'whatsapp_messages' and 'incoming_messages'.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialise le graph, le broker RabbitMQ et le client RPC."""
    logger.info("Orchestrator starting up...")

    # 1. Build LangGraph
    app.state.graph = create_graph()
    logger.info("LangGraph created.")

    # 2. PostgreSQL checkpointer
    async with create_checkpointer(settings.database_url) as checkpointer:
        app.state.graph.checkpointer = checkpointer
        logger.info("Checkpointer ready.")

        # 3. RabbitMQ broker
        broker = MessageBroker()
        await broker.connect(RABBITMQ_URL)
        app.state.broker = broker

        # 4. RPC Client (listens for agent responses)
        rpc_client = RPCClient(broker)
        await rpc_client.start()
        app.state.rpc_client = rpc_client
        logger.info("RPC client started.")

        # 5. Start WhatsApp consumer
        await start_whatsapp_consumer(broker, app.state.graph, rpc_client)
        logger.info("Orchestrator fully started.")

        yield

        # Cleanup
        await broker.disconnect()
        logger.info("Orchestrator shut down.")


app = FastAPI(title="YouCode AI — Orchestrator Service", lifespan=lifespan)


# Keep HTTP endpoint for local debugging without RabbitMQ
@app.post("/api/v1/invoke")
async def invoke_orchestrator(
    payload: IncomingMessage,
    request: Request,
) -> OutgoingResponse:
    """Endpoint HTTP direct (debug/test uniquement)."""
    thread_id = f"orch_{payload.user_id}"
    config = {"configurable": {"thread_id": thread_id}}
    state_update = {
        "messages": [HumanMessage(content=payload.message)],
        "session_id": thread_id,
        "user_id": payload.user_id,
    }

    # Mock staff detection
    staff_phones = ["212600000000", "212600000001", "test_admin"]
    is_staff = any(payload.user_id.startswith(phone) for phone in staff_phones) or "staff" in payload.user_id.lower()
    role = "admin" if payload.user_id.startswith("212600000000") else "formateur"
    
    route = "admin" if is_staff else None
    orch_result = {}

    if not is_staff:
        graph = request.app.state.graph
        orch_result = await graph.ainvoke(state_update, config)
        route = orch_result.get("route", "clarification")

    target_queue = _AGENT_QUEUES.get(route)
    if not target_queue or orch_result.get("active_agent") == "guardrail_refusal":
        messages = orch_result.get("messages", [])
        if messages:
            answer = messages[-1].content
        else:
            final_resp = orch_result.get("final_response", {})
            answer = final_resp.get(
                "answer", "Je ne peux pas répondre à cette demande."
            )
        return OutgoingResponse(
            response=answer,
            active_agent="orchestrator",
            requires_human=False,
        )

    try:
        rpc_client = request.app.state.rpc_client
        result = await resilient_rpc_call(
            rpc_client,
            target_queue,
            {"user_id": payload.user_id, "message": payload.message, "role": role if is_staff else "user"},
            timeout=120.0,
        )
        return OutgoingResponse(
            response=result.get("response", ""),
            active_agent=result.get("active_agent", route),
            requires_human=result.get("requires_human", False),
        )
    except Exception as exc:
        logger.error("RPC call failed: %s", exc)
        fallback = (
            "Le traitement prend plus de temps que prévu."
            if isinstance(exc, TimeoutError)
            else f"Le service {route} est temporairement indisponible."
        )
        return OutgoingResponse(
            response=fallback,
            active_agent="orchestrator",
            requires_human=False,
        )


@app.get("/health")
async def health() -> dict[str, str]:
    return {
        "status": "healthy",
        "service": "orchestrator",
        "version": "3.0.0",
        "pattern": "rpc_async",
    }
