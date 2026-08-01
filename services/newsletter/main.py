"""Newsletter Service — RabbitMQ RPC Server.

Exposes the YouCode Newsletter LangGraph agent as:
1. A RabbitMQ RPC consumer on 'newsletter_requests' queue (for production)
2. An HTTP endpoint at POST /api/v1/invoke (for debug/testing)
"""

import os
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from langchain_core.messages import HumanMessage

from shared.core.config import settings
from shared.infrastructure.database.checkpointer import create_checkpointer
from shared.messaging import MessageBroker, RPCServer
from shared.a2a.schemas import AgentRequest, AgentResponse

from .graph import create_graph

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

RABBITMQ_URL: str = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")


async def handle_newsletter_request(payload: dict) -> dict:
    """Traite une requête Newsletter reçue via RabbitMQ RPC."""
    user_id = payload.get("user_id", "anonymous")
    message = payload.get("message", "")

    graph = app.state.graph
    thread_id = f"newsletter_{user_id}"
    config = {"configurable": {"thread_id": thread_id}}
    state_update = {
        "messages": [HumanMessage(content=message)],
        "session_id": thread_id,
        "user_id": user_id,
    }

    result_state = await graph.ainvoke(state_update, config)

    last_msg = result_state["messages"][-1]
    response_text = (
        last_msg.content if hasattr(last_msg, "content") else str(last_msg)
    )

    return {
        "response": response_text,
        "active_agent": "newsletter",
        "requires_human": False,
    }


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Démarre le graph + le consumer RPC RabbitMQ."""
    async with create_checkpointer(settings.database_url) as checkpointer:
        app.state.graph = create_graph(checkpointer=checkpointer)
        logger.info("Newsletter graph loaded.")

        broker = MessageBroker()
        try:
            await broker.connect(RABBITMQ_URL)
            rpc_server = RPCServer(broker)
            await rpc_server.serve(
                "newsletter_requests",
                handle_newsletter_request,
                prefetch_count=5,
            )
            logger.info("Newsletter RPC server listening on 'newsletter_requests'.")
        except Exception as exc:
            logger.warning("RabbitMQ not available, HTTP-only mode: %s", exc)

        yield

        try:
            await broker.disconnect()
        except Exception:
            pass


app = FastAPI(title="YouCode AI — Newsletter Service", lifespan=lifespan)


@app.post("/api/v1/invoke", response_model=AgentResponse)
async def invoke_newsletter(
    payload: AgentRequest,
    request: Request,
) -> AgentResponse:
    """Endpoint HTTP direct (rétro-compatible, pour debug)."""
    result = await handle_newsletter_request(
        {"user_id": payload.user_id, "message": payload.message}
    )
    return AgentResponse(
        response=result["response"],
        active_agent=result["active_agent"],
        requires_human=result["requires_human"],
    )


@app.get("/health")
async def health() -> dict[str, str]:
    return {
        "status": "healthy",
        "service": "newsletter",
        "version": "3.0.0",
        "pattern": "rpc_async",
    }
