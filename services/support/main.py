"""Support Service — MCP Server.

Exposes the YouCode Support LangGraph agent as a standard
MCP (Model Context Protocol) tool over Streamable HTTP.

The MCP tool ``support_invoke`` handles the full multi-phase
conversation: collecting → awaiting_consent → processing.
LangGraph state is persisted in PostgreSQL via the checkpointer
(keyed by thread_id), so the session survives across calls.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from langchain_core.messages import HumanMessage

from shared.core.config import settings
from shared.infrastructure.database.checkpointer import create_checkpointer
from shared.a2a.schemas import AgentRequest, AgentResponse

from .graph import create_graph


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load the LangGraph checkpointer + compiled graph at startup."""
    async with create_checkpointer(settings.database_url) as checkpointer:
        app.state.graph = create_graph(checkpointer=checkpointer)
        yield


app = FastAPI(title="YouCode AI — Support Service", lifespan=lifespan)


@app.post("/api/v1/invoke", response_model=AgentResponse)
async def invoke_support(
    payload: AgentRequest,
    request: Request,
) -> AgentResponse:
    graph = request.app.state.graph
    thread_id = f"support_{payload.user_id}"

    config = {"configurable": {"thread_id": thread_id}}
    state_update = {
        "messages": [HumanMessage(content=payload.message)],
        "session_id": thread_id,
    }

    result_state = await graph.ainvoke(state_update, config)

    last_message = result_state["messages"][-1]
    response_text = last_message.content if hasattr(last_message, "content") else str(last_message)

    return AgentResponse(
        response=response_text,
        active_agent="support",
        requires_human=False
    )


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "healthy", "service": "support", "version": "2.0.0", "protocol": "a2a"}
