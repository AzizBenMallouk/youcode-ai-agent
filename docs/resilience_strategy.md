# YouCode AI — Resilience & Error Handling Strategy

## Architectural Overview

YouCode AI is a distributed, microservices-based multi-agent architecture designed to process user requests over messaging channels (e.g., WhatsApp). In this architecture:
- **Orchestrator / Gateway**: Receives incoming user messages, manages conversation state, routes requests, and calls remote Agent Services via standard HTTP using the **Agent-to-Agent (A2A)** protocol (JSON-RPC 2.0 formatted payloads).
- **Agent Services** (*Guide Service*, *Support Service*, *Newsletter Service*, *Guardrails Service*): Independent Python microservices powered by LangGraph / Gemini LLM.
- **Persistence Layer**: PostgreSQL checkpointer (AsyncPG) maintaining thread state and conversation history.
- **External AI Infrastructure**: Google Gemini API serving as the primary LLM provider.

Because network calls across microservices and external APIs introduce inherent risks of failure, latency spikes, rate limits, and service outages, YouCode AI implements a comprehensive **Resilience and Error Handling Strategy**.

```mermaid
graph TD
    User([User / WhatsApp]) <--> Gateway[API Gateway / Orchestrator]
    Gateway <-->|A2A HTTP Protocol| Guardrails[Guardrails Service]
    Gateway <-->|A2A HTTP Protocol| Guide[Guide Service]
    Gateway <-->|A2A HTTP Protocol| Support[Support Service]
    Gateway <-->|A2A HTTP Protocol| Newsletter[Newsletter Service]

    subgraph Dependency Boundary
        Guide <-->|AsyncPG| Postgres[(PostgreSQL Checkpointer)]
        Support <-->|AsyncPG| Postgres
        Newsletter <-->|AsyncPG| Postgres
        
        Guide <-->|HTTPS API| Gemini[Google Gemini LLM API]
        Support <-->|HTTPS API| Gemini
        Newsletter <-->|HTTPS API| Gemini
    end
```

---

## 1. Failure Scenarios

### 1.1 Agent Service Down

#### What Happens
The Orchestrator sends an HTTP request to the Support Service (or another remote Agent Service), but the target service is unreachable or down, resulting in a `ConnectionRefusedError`.

#### How We Detect It
The underlying HTTP client (`httpx`) traps the socket failure and raises an `httpx.ConnectError`.

#### How We Respond
1. The Orchestrator catches `httpx.ConnectError`.
2. The retry policy attempts up to 3 connections using exponential backoff.
3. If retries fail, the error is logged with structured context (`service_name`, `user_id`, `thread_id`).
4. The Orchestrator returns a user-friendly message to the client:
   > *"The support service is temporarily unavailable. Please try again in a few minutes."*

```mermaid
sequenceDiagram
    autonumber
    participant Orchestrator
    participant SupportService as Support Service
    participant User

    Orchestrator->>SupportService: HTTP POST /a2a (Request)
    SupportService--XOrchestrator: Connection Refused (ConnectionRefusedError)
    Note over Orchestrator: httpx raises httpx.ConnectError
    Orchestrator->>Orchestrator: Retry Policy (3 attempts with exponential backoff)
    Orchestrator->>Orchestrator: Log structured error (error_type=ConnectError)
    Orchestrator->>User: "The support service is temporarily unavailable. Please try again in a few minutes."
```

---

### 1.2 Gemini API Rate Limit (HTTP 429)

#### What Happens
An agent's LLM call to the Google Gemini API fails due to rate limits or token quota exhaustion (`429 RESOURCE_EXHAUSTED`).

#### How We Detect It
The LangChain Google integration handles the API response and raises a `ChatGoogleGenerativeAIError` with HTTP status code 429.

#### How We Respond
1. The Agent Service catches the 429 exception at the LLM invocation node.
2. The service executes an exponential backoff retry strategy:
   - **Retry 1**: Wait 2 seconds
   - **Retry 2**: Wait 4 seconds
   - **Retry 3**: Wait 8 seconds
3. After 3 failed attempts, the agent halts execution and returns an error response to the Orchestrator.
4. The Orchestrator presents a graceful failure message:
   > *"AI services are temporarily unavailable. Please try again in a few minutes."*

```mermaid
sequenceDiagram
    autonumber
    participant AgentService as Agent Service
    participant GeminiAPI as Gemini LLM API
    participant Orchestrator

    AgentService->>GeminiAPI: Generate Content Request
    GeminiAPI-->>AgentService: HTTP 429 RESOURCE_EXHAUSTED
    Note over AgentService: Trapped ChatGoogleGenerativeAIError (429)
    AgentService->>AgentService: Wait 2s -> Retry 1
    AgentService->>GeminiAPI: Generate Content Request
    GeminiAPI-->>AgentService: HTTP 429 RESOURCE_EXHAUSTED
    AgentService->>AgentService: Wait 4s -> Retry 2
    AgentService->>GeminiAPI: Generate Content Request
    GeminiAPI-->>AgentService: HTTP 429 RESOURCE_EXHAUSTED
    AgentService->>AgentService: Wait 8s -> Retry 3
    AgentService->>GeminiAPI: Generate Content Request
    GeminiAPI-->>AgentService: HTTP 429 RESOURCE_EXHAUSTED
    AgentService-->>Orchestrator: A2A Error Response (Internal Failure)
```

---

### 1.3 PostgreSQL Down

#### What Happens
The LangGraph checkpointer (or service database layer) cannot connect to PostgreSQL to read or write execution state and conversation history.

#### How We Detect It
The AsyncPG connection pool raises an `asyncpg.PostgresConnectionError`.

#### How We Respond
1. All services failing database connectivity respond with HTTP 503 Service Unavailable.
2. The Gateway / Orchestrator catches the error, logs a critical database failure alert, and returns a generic fallback error message to WhatsApp:
   > *"System is undergoing maintenance."*

```mermaid
sequenceDiagram
    autonumber
    participant Gateway as API Gateway / Orchestrator
    participant Agent as Agent Service
    participant Postgres as PostgreSQL DB
    participant User

    Gateway->>Agent: A2A Request
    Agent->>Postgres: Load Checkpoint State
    Postgres--XAgent: Connection Failed (asyncpg.PostgresConnectionError)
    Agent-->>Gateway: HTTP 503 Service Unavailable
    Gateway->>Gateway: Log Critical Error (PostgresConnectionError)
    Gateway-->>User: "System is undergoing maintenance."
```

---

### 1.4 Agent Timeout (> 30 seconds)

#### What Happens
An Agent Service takes too long to process a request (e.g., extended tool execution, multi-step LLM calls, or slow upstream responses), exceeding the threshold.

#### How We Detect It
The Orchestrator's `httpx.AsyncClient` is configured with a 30-second timeout (`timeout=30.0`), which raises an `httpx.TimeoutException` (`httpx.ReadTimeout`).

#### How We Respond
1. The Orchestrator cancels the pending request to avoid holding server resources.
2. The timeout is logged with context details (`service_name`, `user_id`, `thread_id`).
3. The Orchestrator returns a timeout notice to the user:
   > *"Processing is taking longer than expected. Please try again."*

```mermaid
sequenceDiagram
    autonumber
    participant Orchestrator
    participant Agent as Agent Service
    participant User

    Orchestrator->>Agent: HTTP POST /a2a (Request)
    Note over Agent: Processing takes > 30 seconds
    Note over Orchestrator: Timeout timer (30s) expires
    Orchestrator->>Orchestrator: Raise httpx.TimeoutException & Cancel Request
    Orchestrator->>Orchestrator: Log structured error (error_type=TimeoutException)
    Orchestrator->>User: "Processing is taking longer than expected. Please try again."
```

---

### 1.5 Invalid A2A Response

#### What Happens
An Agent Service returns a malformed JSON response or a non-compliant JSON-RPC response payload.

#### How We Detect It
Pydantic validation fails when attempting to parse the incoming response payload into the `A2AResponse` model, raising a `pydantic.ValidationError`.

#### How We Respond
1. The Orchestrator traps the `ValidationError`.
2. The error and raw response payload are logged for investigation.
3. The Orchestrator returns a generic failure message to the user:
   > *"An unexpected response was received from the processing service. Please try again."*

```mermaid
sequenceDiagram
    autonumber
    participant Orchestrator
    participant Agent as Agent Service
    participant User

    Orchestrator->>Agent: HTTP POST /a2a
    Agent-->>Orchestrator: HTTP 200 OK {"malformed": "json"}
    Orchestrator->>Orchestrator: Parse with Pydantic A2AResponse
    Note over Orchestrator: Raises pydantic.ValidationError
    Orchestrator->>Orchestrator: Log raw payload & validation error
    Orchestrator-->>User: "An unexpected response was received from the processing service. Please try again."
```

---

## 2. Retry Policy

YouCode AI uses **Tenacity** alongside **httpx** to handle retries for inter-service HTTP communications cleanly and predictably.

### Python Code Implementation

```python
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)
import httpx


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((httpx.ConnectError, httpx.TimeoutException)),
)
async def call_agent(url: str, payload: dict) -> dict:
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(url, json=payload)
        response.raise_for_status()
        return response.json()
```

### Configuration Parameter Breakdown

| Parameter | Configuration | Explanation |
| :--- | :--- | :--- |
| **`stop`** | `stop_after_attempt(3)` | Limits execution to **3 total attempts** (1 initial call + 2 retries). This caps maximum latency and prevents runaway retries during prolonged outages. |
| **`wait`** | `wait_exponential(multiplier=1, min=2, max=10)` | Applies an **exponential backoff delay** ($T = \text{multiplier} \times 2^{\text{attempt}}$). Retries wait **2s**, then **4s**, up to a maximum delay capped at **10s**. This prevents thundering herd issues on recovering services. |
| **`retry`** | `retry_if_exception_type((httpx.ConnectError, httpx.TimeoutException))` | Restricts retries strictly to transient network-level errors: connection refusal (`ConnectError`) and request timeouts (`TimeoutException`). Non-transient errors (such as HTTP 400 or 401) fail immediately without retrying. |
| **`timeout`** | `timeout=30.0` | Sets an explicit **30-second timeout** on `httpx.AsyncClient`. Ensures that unresponsive service requests are aborted promptly rather than hanging indefinitely. |
| **`raise_for_status()`** | `response.raise_for_status()` | Raises an `httpx.HTTPStatusError` for HTTP status codes in the 4xx and 5xx ranges, ensuring downstream errors are properly flagged. |

---

## 3. Graceful Degradation

If a microservice or external component experiences an outage, YouCode AI limits the failure impact so unimpacted system functionality remains available.

| Failed Component | Impact | User Experience |
| :--- | :--- | :--- |
| **Guide Service Down** | Cannot answer questions | *"I cannot answer your question right now. Please try again later."* |
| **Support Service Down** | Cannot process requests | *"Support requests are temporarily unavailable."* |
| **Newsletter Down** | Cannot manage subscriptions | *"Newsletter service is currently offline."* |
| **PostgreSQL Down** | No service works | *"System is undergoing maintenance."* |
| **Gemini API Down** | All agents fail | *"AI services are temporarily unavailable."* |

> [!NOTE]
> **Isolation Principle**: Outages in specialized agent microservices (e.g., Newsletter Service) must be caught at the Orchestrator level to ensure core routing and other agent capabilities remain functional.

---

## 4. Logging and Monitoring

### Structured Error Logging

All errors across YouCode AI microservices are output as structured JSON objects to `stdout`. This standardizes logs for aggregation tools (such as Datadog, Grafana Loki, or ELK).

#### Mandatory Log Attributes

Every error log entry **must** include the following key fields:
- `timestamp`: ISO-8601 UTC timestamp.
- `service_name`: Name of the emitting microservice (e.g., `orchestrator`, `support-service`).
- `error_type`: Class name of the exception caught (e.g., `ConnectError`, `PostgresConnectionError`, `ValidationError`).
- `user_id`: Identifier of the user associated with the request.
- `thread_id`: Conversation thread identifier.

#### Example JSON Log Payload

```json
{
  "timestamp": "2026-07-26T18:23:44Z",
  "service_name": "orchestrator",
  "error_type": "ConnectError",
  "user_id": "user_12345",
  "thread_id": "thread_abc987",
  "level": "ERROR",
  "message": "Failed to connect to Support Service at http://support-service:8002/a2a",
  "details": {
    "target_url": "http://support-service:8002/a2a",
    "attempt": 3,
    "exception": "httpx.ConnectError: [Errno 111] Connection refused"
  }
}
```

### Observability & Tracing Recommendations

> [!TIP]
> **LangSmith Recommendation**: Integrating LangSmith provides end-to-end tracing for LLM calls, step-by-step node execution visualizations in LangGraph, latency analysis, and token consumption tracking.

1. **LangSmith Integration (Future / Recommended)**:
   - Enable via environment variables (`LANGCHAIN_TRACING_V2=true`, `LANGCHAIN_API_KEY=<key>`).
   - Captures inputs, outputs, prompts, latencies, and tool execution traces across all agent services.
2. **Structured Log Aggregation**:
   - Stream JSON formatted stdout logs into centralized logging platforms.
   - Set up automated alerts for high error rates, consecutive retry failures, or database connection pool exhaustion.

---

## 5. Health Checks

### GET /health Specification

Each microservice exposes an unauthenticated health probe at `GET /health`.

#### Endpoint Output

```json
{
  "status": "healthy",
  "service": "support",
  "version": "1.0.0",
  "postgres": "connected",
  "gemini": "available"
}
```

### Docker Compose Healthcheck Integration

Docker Compose uses the `GET /health` endpoint to monitor container health and control startup dependency order via `depends_on` with `service_healthy`.

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: youcode_db
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: secretpassword
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres -d youcode_db"]
      interval: 5s
      timeout: 5s
      retries: 5
      start_period: 10s

  support-service:
    build:
      context: .
      dockerfile: Dockerfile.api
    command: uvicorn youcode_ai.agents.support.service:app --host 0.0.0.0 --port 8002
    ports:
      - "8002:8002"
    environment:
      DATABASE_URL: postgresql+asyncpg://postgres:secretpassword@postgres:5432/youcode_db
      GEMINI_API_KEY: ${GEMINI_API_KEY}
    depends_on:
      postgres:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8002/health"]
      interval: 10s
      timeout: 5s
      retries: 3
      start_period: 15s

  orchestrator:
    build:
      context: .
      dockerfile: Dockerfile.api
    command: uvicorn youcode_ai.orchestrator:app --host 0.0.0.0 --port 8000
    ports:
      - "8000:8000"
    environment:
      SUPPORT_SERVICE_URL: http://support-service:8002/a2a
    depends_on:
      postgres:
        condition: service_healthy
      support-service:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 10s
      timeout: 5s
      retries: 3
      start_period: 15s
```
