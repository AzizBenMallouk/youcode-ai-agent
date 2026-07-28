import logging
from typing import Any

import httpx

from .schemas import AgentRequest, AgentResponse

logger = logging.getLogger(__name__)

class A2AClient:
    """Client for Agent-to-Agent communication over HTTP."""

    def __init__(self, base_url: str, timeout: float = 30.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    async def invoke(
        self,
        user_id: str,
        message: str,
        metadata: dict[str, Any] | None = None
    ) -> AgentResponse:
        """Invokes another agent service."""
        request_data = AgentRequest(
            user_id=user_id,
            message=message,
            metadata=metadata or {}
        )
        
        endpoint = f"{self.base_url}/api/v1/invoke"
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    endpoint,
                    json=request_data.model_dump()
                )
                response.raise_for_status()
                return AgentResponse.model_validate(response.json())
        except httpx.HTTPError as e:
            logger.error(f"Error calling agent at {endpoint}: {e}")
            raise
