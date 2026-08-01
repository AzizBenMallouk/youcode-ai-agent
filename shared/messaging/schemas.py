"""Schémas de messages pour la communication inter-services."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class AgentTaskMessage(BaseModel):
    """Message envoyé par l'Orchestrateur à un agent."""

    correlation_id: str
    user_id: str
    message: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class AgentTaskResult(BaseModel):
    """Réponse envoyée par un agent à l'Orchestrateur."""

    correlation_id: str
    response: str
    active_agent: str
    requires_human: bool = False
    error: str | None = None
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
