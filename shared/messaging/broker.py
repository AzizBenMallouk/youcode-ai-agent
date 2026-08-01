"""Client RabbitMQ partagé avec gestion du cycle de vie."""

from __future__ import annotations

import json
import logging
from typing import Any, Callable, Awaitable

import aio_pika
from aio_pika.abc import (
    AbstractRobustConnection,
    AbstractRobustChannel,
    AbstractIncomingMessage,
)

logger = logging.getLogger(__name__)


class MessageBroker:
    """Gère la connexion RabbitMQ et les opérations de messaging."""

    def __init__(self) -> None:
        self._connection: AbstractRobustConnection | None = None
        self._channel: AbstractRobustChannel | None = None

    @property
    def is_connected(self) -> bool:
        return self._connection is not None and not self._connection.is_closed

    async def connect(self, url: str) -> None:
        """Établit une connexion robuste à RabbitMQ."""
        logger.info("Connecting to RabbitMQ at %s", url.split('@')[-1])
        self._connection = await aio_pika.connect_robust(url)
        self._channel = await self._connection.channel()
        logger.info("RabbitMQ connection established.")

    async def disconnect(self) -> None:
        """Ferme proprement la connexion."""
        if self._connection and not self._connection.is_closed:
            await self._connection.close()
            logger.info("RabbitMQ connection closed.")
        self._connection = None
        self._channel = None

    async def declare_queue(
        self,
        name: str,
        *,
        durable: bool = True,
        with_dlq: bool = False,
        message_ttl: int | None = None,
        exclusive: bool = False,
        auto_delete: bool = False,
    ) -> aio_pika.abc.AbstractRobustQueue:
        """Déclare une queue avec DLQ optionnelle."""
        if not self._channel:
            raise RuntimeError("Broker not connected.")

        arguments: dict[str, Any] = {}

        if with_dlq:
            dlq_name = f"{name}_dlq"
            await self._channel.declare_queue(dlq_name, durable=True)
            arguments["x-dead-letter-exchange"] = ""
            arguments["x-dead-letter-routing-key"] = dlq_name
            logger.info("Declared DLQ: %s", dlq_name)

        if message_ttl is not None:
            arguments["x-message-ttl"] = message_ttl

        queue = await self._channel.declare_queue(
            name,
            durable=durable,
            exclusive=exclusive,
            auto_delete=auto_delete,
            arguments=arguments or None,
        )
        logger.info("Declared queue: %s (durable=%s, dlq=%s)", name, durable, with_dlq)
        return queue

    async def publish(
        self,
        queue_name: str,
        body: dict[str, Any],
        *,
        correlation_id: str | None = None,
        reply_to: str | None = None,
    ) -> None:
        """Publie un message JSON dans une queue."""
        if not self._channel:
            raise RuntimeError("Broker not connected.")

        message = aio_pika.Message(
            body=json.dumps(body, default=str).encode(),
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            correlation_id=correlation_id,
            reply_to=reply_to,
        )

        await self._channel.default_exchange.publish(
            message,
            routing_key=queue_name,
        )

    async def set_qos(self, prefetch_count: int = 1) -> None:
        """Configure le prefetch count pour le consumer."""
        if not self._channel:
            raise RuntimeError("Broker not connected.")
        await self._channel.set_qos(prefetch_count=prefetch_count)

    async def consume(
        self,
        queue_name: str,
        callback: Callable[[AbstractIncomingMessage], Awaitable[None]],
        *,
        prefetch_count: int = 1,
        with_dlq: bool = False,
        exclusive: bool = False,
        auto_delete: bool = False,
    ) -> None:
        """Démarre un consumer sur une queue."""
        if not self._channel:
            raise RuntimeError("Broker not connected.")

        await self._channel.set_qos(prefetch_count=prefetch_count)
        queue = await self.declare_queue(
            queue_name, 
            with_dlq=with_dlq,
            exclusive=exclusive,
            auto_delete=auto_delete,
        )
        await queue.consume(callback)
        logger.info("Consumer started on queue: %s (prefetch=%d)", queue_name, prefetch_count)
