"""
Conversation Memory Summarizer.

When the conversation history exceeds `memory_summary_threshold` messages,
the oldest messages are summarized by the LLM into a single SystemMessage.
The most recent `memory_keep_recent` messages are always kept verbatim.

This prevents context window overflow in long conversations while preserving
critical information (names, emails, dates, decisions) extracted earlier.

Usage:
    from shared.memory import summarize_if_needed
    from shared.core.llm import create_chat_model

    history = await summarize_if_needed(messages, llm=create_chat_model(use_cache=False))
"""

import logging
from typing import Sequence

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
)

from shared.core.config import settings

logger = logging.getLogger(__name__)

_SUMMARY_PROMPT = """You are a conversation memory assistant.
Summarize the key facts from the conversation below in 3-5 concise sentences.
Preserve ALL critical data: names, emails, phone numbers, dates, campus, decisions, and consent status.
Write in the same language as the conversation (French, English, Arabic, or Darija).
Do NOT add opinions or interpretations.

Conversation to summarize:
{conversation}
"""


def _format_messages_for_summary(messages: Sequence[BaseMessage]) -> str:
    """Format a list of messages into a readable string for the LLM."""
    lines: list[str] = []
    for msg in messages:
        role = "User" if isinstance(msg, HumanMessage) else "Assistant"
        content = msg.content if isinstance(msg.content, str) else str(msg.content)
        lines.append(f"{role}: {content}")
    return "\n".join(lines)


async def summarize_if_needed(
    messages: list[BaseMessage],
    llm: BaseChatModel | None = None,
    threshold: int | None = None,
    keep_recent: int | None = None,
) -> list[BaseMessage]:
    """
    Summarize old messages if history exceeds the threshold.

    Args:
        messages:     Full conversation history.
        llm:          LLM to use for summarization. Defaults to create_chat_model(use_cache=False).
        threshold:    Trigger summarization when len(messages) > threshold.
                      Defaults to settings.memory_summary_threshold.
        keep_recent:  Number of recent messages to keep verbatim.
                      Defaults to settings.memory_keep_recent.

    Returns:
        A list where old messages are replaced by a single SystemMessage summary,
        followed by the most recent `keep_recent` messages unchanged.
        If below threshold, returns the original list unchanged.
    """
    effective_threshold = threshold if threshold is not None else settings.memory_summary_threshold
    effective_keep = keep_recent if keep_recent is not None else settings.memory_keep_recent

    # No summarization needed
    if len(messages) <= effective_threshold:
        return messages

    old_messages = messages[:-effective_keep]
    recent_messages = messages[-effective_keep:]

    logger.info(
        "Summarizing %d old messages (keeping %d recent).",
        len(old_messages),
        effective_keep,
    )

    # Lazy import to avoid circular imports at module load time
    if llm is None:
        from shared.core.llm import create_chat_model
        llm = create_chat_model(use_cache=False)

    try:
        conversation_text = _format_messages_for_summary(old_messages)
        prompt = _SUMMARY_PROMPT.format(conversation=conversation_text)
        summary_response = await llm.ainvoke([HumanMessage(content=prompt)])
        summary_text = summary_response.content

        logger.info("Summary generated (%d chars).", len(summary_text))

        summary_message = SystemMessage(
            content=f"[Résumé de la conversation précédente]\n{summary_text}"
        )
        return [summary_message] + list(recent_messages)

    except Exception:
        # If summarization fails, fall back to a simple truncation to avoid breaking the agent
        logger.exception(
            "Summarization failed — falling back to truncation (%d messages).",
            effective_keep,
        )
        return list(recent_messages)


def summarize_if_needed_sync(
    messages: list[BaseMessage],
    llm: BaseChatModel | None = None,
    threshold: int | None = None,
    keep_recent: int | None = None,
) -> list[BaseMessage]:
    """
    Synchronous wrapper around summarize_if_needed.

    Use this in synchronous node functions (e.g., LangGraph nodes that are not async).
    Falls back to simple truncation if above threshold (no LLM call in sync context).
    """
    effective_threshold = threshold if threshold is not None else settings.memory_summary_threshold
    effective_keep = keep_recent if keep_recent is not None else settings.memory_keep_recent

    if len(messages) <= effective_threshold:
        return messages

    # In sync context we can't await, so we do a simple truncation
    # The async version (summarize_if_needed) should be preferred when possible
    logger.warning(
        "Sync summarization: falling back to truncation (%d → %d messages).",
        len(messages),
        effective_keep,
    )
    return list(messages[-effective_keep:])
