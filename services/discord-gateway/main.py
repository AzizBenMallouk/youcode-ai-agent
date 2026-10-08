"""Discord Gateway Service.

Bridges Discord channels with the YouCode AI agent pipeline.

Incoming Discord messages → published to RabbitMQ `incoming_messages` queue.
Outbound responses from `outbound_messages` queue → sent to the correct Discord channel.

The message envelope includes a `source` field so the Orchestrator and
the WhatsApp gateway ignore messages not intended for them.
"""

import asyncio
import json
import logging
import os
from contextlib import asynccontextmanager

import aio_pika
import discord
from fastapi import FastAPI

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
RABBITMQ_URL: str = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")
DISCORD_BOT_TOKEN: str = os.getenv("DISCORD_BOT_TOKEN", "")


SOURCE = "discord"

# ---------------------------------------------------------------------------
# RabbitMQ client
# ---------------------------------------------------------------------------
class RabbitMQClient:
    connection: aio_pika.RobustConnection | None = None
    channel: aio_pika.RobustChannel | None = None


mq = RabbitMQClient()


async def connect_rabbitmq() -> None:
    mq.connection = await aio_pika.connect_robust(RABBITMQ_URL)
    mq.channel = await mq.connection.channel()

    # Ensure queues exist
    await mq.channel.declare_queue("incoming_messages", durable=True)
    await mq.channel.declare_queue("outbound_messages", durable=True)
    logger.info("RabbitMQ connected for Discord gateway.")


async def publish_incoming(user_id: str, channel_id: int, text: str) -> None:
    """Publish a Discord message to the shared incoming queue."""
    if not mq.channel:
        logger.error("RabbitMQ not connected — cannot publish Discord message.")
        return

    payload = {
        "source": SOURCE,
        "instance": str(channel_id),   # channel acts as the "instance"
        "user_id": str(user_id),
        "message": text,
    }
    await mq.channel.default_exchange.publish(
        aio_pika.Message(
            body=json.dumps(payload).encode(),
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
        ),
        routing_key="incoming_messages",
    )
    logger.info("Discord message from %s published to incoming_messages.", user_id)


# ---------------------------------------------------------------------------
# Discord Bot
# ---------------------------------------------------------------------------
intents = discord.Intents.default()
intents.message_content = True
bot = discord.Client(intents=intents)


@bot.event
async def on_ready() -> None:
    logger.info("Discord bot connected as %s", bot.user)


@bot.event
async def on_message(message: discord.Message) -> None:
    # Ignore own messages
    if message.author == bot.user:
        return

    # Only respond to Direct Messages (1:1 private conversations)
    if not isinstance(message.channel, discord.DMChannel):
        logger.debug("Ignoring non-DM message from %s in channel %s", message.author, message.channel)
        return

    if not message.content.strip():
        return

    await publish_incoming(
        user_id=str(message.author.id),
        channel_id=message.channel.id,
        text=message.content.strip(),
    )


async def send_discord_message(channel_id: int, text: str) -> None:
    """Send a reply to a Discord channel."""
    channel = bot.get_channel(channel_id)
    if channel is None:
        try:
            channel = await bot.fetch_channel(channel_id)
        except Exception as exc:
            logger.error("Cannot fetch Discord channel %d: %s", channel_id, exc)
            return

    try:
        # Discord has a 2000 char limit — split if needed
        if len(text) <= 2000:
            await channel.send(text)
        else:
            for i in range(0, len(text), 1990):
                await channel.send(text[i : i + 1990])
    except Exception as exc:
        logger.error("Failed to send Discord message to channel %d: %s", channel_id, exc)


async def start_outbound_consumer() -> None:
    """Consume outbound_messages and forward Discord-destined messages."""
    if not mq.channel:
        return

    queue = await mq.channel.declare_queue("outbound_messages", durable=True)

    async def on_outbound(msg: aio_pika.abc.AbstractIncomingMessage) -> None:
        async with msg.process():
            try:
                payload = json.loads(msg.body.decode())

                # Only handle messages meant for Discord
                if payload.get("source") != SOURCE:
                    return

                channel_id = int(payload.get("instance", 0))
                text = payload.get("text", "")

                if channel_id and text:
                    await send_discord_message(channel_id, text)
            except Exception as exc:
                logger.error("Error processing outbound Discord message: %s", exc)

    await queue.consume(on_outbound)
    logger.info("Discord outbound consumer started on 'outbound_messages'.")


# ---------------------------------------------------------------------------
# FastAPI lifespan
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    if not DISCORD_BOT_TOKEN:
        logger.warning(
            "DISCORD_BOT_TOKEN not set — Discord gateway running in stub mode (no bot)."
        )
    else:
        await connect_rabbitmq()
        await start_outbound_consumer()

        # Run Discord bot in background task
        asyncio.create_task(bot.start(DISCORD_BOT_TOKEN))
        logger.info("Discord bot starting in background...")

    yield

    if bot.is_ready():
        await bot.close()
    if mq.connection:
        await mq.connection.close()
    logger.info("Discord gateway shut down.")


app = FastAPI(title="YouCode AI — Discord Gateway", lifespan=lifespan)


@app.get("/health")
async def health() -> dict:
    return {
        "status": "healthy",
        "service": "discord-gateway",
        "bot_connected": bot.is_ready(),
    }
