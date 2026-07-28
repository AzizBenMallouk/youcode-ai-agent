"""Async MCP agent client for inter-service communication.

Replaces the custom A2A HTTP protocol with the standard
Model Context Protocol (MCP) over Streamable HTTP.
"""

from __future__ import annotations

import logging
from contextlib import AsyncExitStack
from typing import Any

import httpx
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

logger = logging.getLogger(__name__)


class MCPAgentClient:
    """Async context manager that connects to a remote MCP agent server
    and exposes a simple ``call_tool`` interface.

    Usage
    -----
    async with MCPAgentClient("http://support:8002") as client:
        result = await client.call_tool(
            "support_invoke",
            message_text="...",
            thread_id="...",
            user_id="...",
        )
    """

    def __init__(
        self,
        agent_base_url: str,
        *,
        timeout: float = 60.0,
    ) -> None:
        self._mcp_url = f"{agent_base_url.rstrip('/')}/mcp"
        self._timeout = timeout
        self._session: ClientSession | None = None
        self._exit_stack: AsyncExitStack | None = None

    async def __aenter__(self) -> "MCPAgentClient":
        self._exit_stack = AsyncExitStack()
        try:
            http_client = httpx.AsyncClient(timeout=self._timeout)
            transport = await self._exit_stack.enter_async_context(
                streamable_http_client(
                    self._mcp_url,
                    http_client=http_client,
                )
            )
            # streamable_http_client yields (read, write, get_session_id)
            read, write, _ = transport
            self._session = await self._exit_stack.enter_async_context(
                ClientSession(read, write)
            )
            await self._session.initialize()
        except Exception:
            await self._exit_stack.aclose()
            raise
        return self

    async def __aexit__(self, *args: Any) -> None:
        if self._exit_stack:
            await self._exit_stack.aclose()
        self._session = None

    async def call_tool(
        self,
        tool_name: str,
        **kwargs: Any,
    ) -> str:
        """Call a tool on the remote MCP agent and return the text result."""
        if self._session is None:
            raise RuntimeError("MCPAgentClient must be used as async context manager")

        logger.info("MCP call → %s::%s", self._mcp_url, tool_name)
        result = await self._session.call_tool(tool_name, kwargs)

        # Extract first text content block
        for content in result.content:
            if hasattr(content, "text"):
                return content.text

        return ""


async def call_agent_tool(
    agent_base_url: str,
    tool_name: str,
    *,
    timeout: float = 60.0,
    **kwargs: Any,
) -> str:
    """Convenience one-shot helper — opens a session, calls the tool, closes.

    Use this for simple calls from the Orchestrator.
    Raises on connection/timeout errors (caller handles fallback).
    """
    async with MCPAgentClient(agent_base_url, timeout=timeout) as client:
        return await client.call_tool(tool_name, **kwargs)
