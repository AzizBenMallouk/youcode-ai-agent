"""Patterns de résilience : Circuit Breaker et Retry."""

from __future__ import annotations

import logging
from typing import Any

from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
)

from .rpc import RPCClient

logger = logging.getLogger(__name__)


def create_resilient_rpc_call(
    *,
    max_attempts: int = 3,
    min_wait: float = 1.0,
    max_wait: float = 30.0,
):
    """Crée un wrapper d'appel RPC avec retry et exponential backoff."""

    @retry(
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(multiplier=1, min=min_wait, max=max_wait),
        retry=retry_if_exception_type((TimeoutError, ConnectionError, OSError)),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )
    async def resilient_call(
        rpc_client: RPCClient,
        queue: str,
        payload: dict[str, Any],
        *,
        timeout: float = 120.0,
    ) -> dict[str, Any]:
        """Appel RPC avec retry automatique."""
        return await rpc_client.call(queue, payload, timeout=timeout)

    return resilient_call


# Instance par défaut prête à l'emploi
resilient_rpc_call = create_resilient_rpc_call()
