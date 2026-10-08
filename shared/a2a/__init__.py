"""Shared HTTP endpoint schemas (AgentRequest / AgentResponse).

The old A2A HTTP direct-call client has been removed.
Inter-agent communication now uses RabbitMQ RPC (shared.messaging).
These schemas remain only for the /api/v1/invoke debug HTTP endpoints.
"""
