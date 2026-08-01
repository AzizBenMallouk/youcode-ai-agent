"""Pattern RPC (Request/Reply) au-dessus de RabbitMQ.

RPCClient : utilisé par l'Orchestrateur pour envoyer des requêtes
            et attendre les réponses.
RPCServer : utilisé par les Agents pour consommer et répondre.
"""

from __future__ import annotations

import asyncio
import json
import logging
import uuid
from typing import Any, Callable, Awaitable

import aio_pika
from aio_pika.abc import AbstractIncomingMessage

from .broker import MessageBroker

logger = logging.getLogger(__name__)


class RPCClient:
    """Client RPC — envoie des requêtes aux agents et attend les réponses.

    Utilisé côté Orchestrateur.
    """

    def __init__(self, broker: MessageBroker) -> None:
        self._broker = broker
        # Each client instance needs its own unique queue for replies
        # to prevent round-robin routing of responses across replicas.
        self.RESPONSE_QUEUE = f"agent_responses_{uuid.uuid4().hex}"
        self._futures: dict[str, asyncio.Future[dict[str, Any]]] = {}
        self._consumer_started = False

    async def start(self) -> None:
        """Démarre le consumer sur la queue de réponses."""
        if self._consumer_started:
            return

        await self._broker.declare_queue(
            self.RESPONSE_QUEUE,
            durable=False,
            exclusive=True,
            auto_delete=True,
        )
        await self._broker.consume(
            self.RESPONSE_QUEUE,
            self._on_response,
            prefetch_count=50,
            exclusive=True,
            auto_delete=True,
        )
        self._consumer_started = True
        logger.info("RPCClient response consumer started on '%s'", self.RESPONSE_QUEUE)

    async def call(
        self,
        queue: str,
        payload: dict[str, Any],
        *,
        timeout: float = 120.0,
    ) -> dict[str, Any]:
        """Envoie une requête à un agent et attend la réponse."""
        correlation_id = str(uuid.uuid4())

        future: asyncio.Future[dict[str, Any]] = asyncio.get_event_loop().create_future()
        self._futures[correlation_id] = future

        await self._broker.publish(
            queue,
            {**payload, "correlation_id": correlation_id},
            correlation_id=correlation_id,
            reply_to=self.RESPONSE_QUEUE,
        )
        logger.info(
            "RPC request sent to '%s' (correlation_id=%s)",
            queue,
            correlation_id,
        )

        try:
            result = await asyncio.wait_for(future, timeout=timeout)
        except asyncio.TimeoutError:
            self._futures.pop(correlation_id, None)
            logger.error(
                "RPC timeout for correlation_id=%s on queue '%s'",
                correlation_id,
                queue,
            )
            raise TimeoutError(
                f"Agent on queue '{queue}' did not respond within {timeout}s"
            )

        return result

    async def _on_response(self, message: AbstractIncomingMessage) -> None:
        """Callback pour les messages de réponse."""
        async with message.process():
            correlation_id = message.correlation_id
            if not correlation_id:
                logger.warning("Received response without correlation_id, ignoring.")
                return

            future = self._futures.pop(correlation_id, None)
            if future is None:
                logger.warning(
                    "Received response for unknown correlation_id=%s (possibly timed out)",
                    correlation_id,
                )
                return

            try:
                body = json.loads(message.body.decode())
            except (json.JSONDecodeError, UnicodeDecodeError) as exc:
                future.set_exception(RuntimeError(f"Invalid response body: {exc}"))
                return

            if not future.done():
                future.set_result(body)
                logger.info("RPC response received for correlation_id=%s", correlation_id)


class RPCServer:
    """Serveur RPC — consomme des requêtes et publie les réponses.

    Utilisé côté Agents (Guide, Support, Newsletter).
    """

    def __init__(self, broker: MessageBroker) -> None:
        self._broker = broker

    async def serve(
        self,
        queue: str,
        handler: Callable[[dict[str, Any]], Awaitable[dict[str, Any]]],
        *,
        prefetch_count: int = 5,
        with_dlq: bool = True,
    ) -> None:
        """Démarre le consumer RPC sur une queue."""
        await self._broker.declare_queue(
            queue,
            durable=True,
            with_dlq=with_dlq,
        )

        async def on_request(message: AbstractIncomingMessage) -> None:
            async with message.process():
                correlation_id = message.correlation_id
                reply_to = message.reply_to

                if not correlation_id or not reply_to:
                    logger.warning(
                        "RPC request missing correlation_id or reply_to, ignoring."
                    )
                    return

                try:
                    payload = json.loads(message.body.decode())
                except (json.JSONDecodeError, UnicodeDecodeError) as exc:
                    logger.error("Invalid RPC request body: %s", exc)
                    error_response = {
                        "correlation_id": correlation_id,
                        "response": "Erreur interne de traitement.",
                        "active_agent": "unknown",
                        "error": str(exc),
                    }
                    await self._broker.publish(
                        reply_to,
                        error_response,
                        correlation_id=correlation_id,
                    )
                    return

                logger.info(
                    "RPC request received on '%s' (correlation_id=%s)",
                    queue,
                    correlation_id,
                )

                try:
                    result = await handler(payload)
                except Exception as exc:
                    logger.exception(
                        "RPC handler failed for correlation_id=%s: %s",
                        correlation_id,
                        exc,
                    )
                    result = {
                        "response": "Une erreur est survenue lors du traitement.",
                        "active_agent": "unknown",
                        "error": str(exc),
                    }

                result["correlation_id"] = correlation_id

                await self._broker.publish(
                    reply_to,
                    result,
                    correlation_id=correlation_id,
                )
                logger.info(
                    "RPC response sent for correlation_id=%s",
                    correlation_id,
                )

        await self._broker.consume(
            queue,
            on_request,
            prefetch_count=prefetch_count,
            with_dlq=with_dlq,
        )
        logger.info(
            "RPCServer listening on '%s' (prefetch=%d)",
            queue,
            prefetch_count,
        )
