"""Orchestrator Service — MCP Client.

Receives messages from the Gateway, runs the Supervisor/Guardrail
LangGraph to determine the correct agent, then delegates to
the agent via MCP (Model Context Protocol) over Streamable HTTP.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from langchain_core.messages import HumanMessage

from shared.core.config import settings
from shared.infrastructure.database.checkpointer import create_checkpointer
from shared.a2a.client import A2AClient

from .graph import create_graph
from .schemas import IncomingMessage, OutgoingResponse

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Agent URL map (resolved from settings — works in Docker or on remote hosts)
# ---------------------------------------------------------------------------
_AGENT_URLS: dict[str, str] = {
    "guide": settings.guide_url,
    "support": settings.support_url,
    "newsletter": settings.newsletter_url,
}


# ---------------------------------------------------------------------------
# Lifespan — compile Orchestrator graph with PostgreSQL checkpointer
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.graph = create_graph()
    async with create_checkpointer(settings.database_url) as checkpointer:
        app.state.graph.checkpointer = checkpointer
        yield


# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------

app = FastAPI(title="YouCode AI — Orchestrator Service", lifespan=lifespan)


@app.post("/api/v1/invoke")
async def invoke_orchestrator(
    payload: IncomingMessage,
    request: Request,
) -> OutgoingResponse:
    # 1. Run the Supervisor/Guardrail graph to decide the route
    thread_id = f"orch_{payload.user_id}"
    config = {"configurable": {"thread_id": thread_id}}
    state_update = {
        "messages": [HumanMessage(content=payload.message)],
        "session_id": thread_id,
        "user_id": payload.user_id,
    }

    graph = request.app.state.graph
    orch_result = await graph.ainvoke(state_update, config)
    route = orch_result.get("route", "clarification")

    # 2. Handle instant responses (guardrail refusal / clarification / out_of_scope)
    target_url = _AGENT_URLS.get(route)
    if not target_url or orch_result.get("active_agent") == "guardrail_refusal":
        messages = orch_result.get("messages", [])
        if messages:
            answer = messages[-1].content
        else:
            final_response = orch_result.get("final_response", {})
            answer = final_response.get("answer", "Je ne peux pas répondre à cette demande.")
        return OutgoingResponse(
            response=answer,
            active_agent="orchestrator",
            requires_human=False,
        )

    # 3. Delegate to the target agent via A2A
    try:
        a2a_client = A2AClient(base_url=target_url, timeout=60.0)
        agent_resp = await a2a_client.invoke(
            user_id=payload.user_id,
            message=payload.message,
            metadata={"source": "orchestrator"}
        )
        response_text = agent_resp.response
    except Exception as exc:
        logger.error("A2A call to %s failed: %s", route, exc)
        fallback = (
            "Le traitement prend plus de temps que prévu. Veuillez réessayer."
            if "timeout" in str(exc).lower()
            else f"Le service {route} est temporairement indisponible."
        )
        return OutgoingResponse(
            response=fallback,
            active_agent="orchestrator",
            requires_human=False,
        )

    return OutgoingResponse(
        response=response_text,
        active_agent=route,
        requires_human=False,
    )


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "healthy", "service": "orchestrator", "version": "2.0.0", "protocol": "a2a"}
