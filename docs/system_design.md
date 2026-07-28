# YouCode AI Platform - System Architecture & Workflows

Here are the diagrams that explain the inner workings of your application. These diagrams use Mermaid.js and are rendered natively.

## 1. High-Level System Architecture
This diagram shows how all the microservices, external APIs, and databases communicate with each other.

```mermaid
graph TD
    %% External Entities
    User((WhatsApp User))
    GoogleSheets[(Google Sheets)]
    
    %% Gateway & WhatsApp
    EvoAPI[Evolution API<br/>port: 8090]
    Gateway[Gateway Service<br/>Webhook Receiver]
    
    %% Orchestration
    Orchestrator{Orchestrator<br/>Router LLM}
    
    %% Agents
    AgentSupport[Support Agent<br/>LangGraph]
    AgentGuide[Guide Agent<br/>RAG / LangGraph]
    AgentNews[Newsletter Agent<br/>LangGraph]
    
    %% Databases & Storage
    Postgres[(PostgreSQL<br/>SQLAlchemy)]
    Qdrant[(Qdrant<br/>Vector DB)]
    Redis[(Redis)]
    
    %% MCP Servers
    SheetMCP[[Sheet GMCP<br/>FastMCP Server]]

    %% Flows
    User <-->|Messages| EvoAPI
    EvoAPI -->|messages.upsert<br/>Webhook| Gateway
    Gateway -->|Invoke API| Orchestrator
    Orchestrator -->|HTTP/JSON| Gateway
    Gateway -->|Send Reply| EvoAPI
    EvoAPI --- Redis
    EvoAPI --- Postgres

    %% Routing
    Orchestrator -->|Route: support| AgentSupport
    Orchestrator -->|Route: guide| AgentGuide
    Orchestrator -->|Route: newsletter| AgentNews

    %% Agent Dependencies
    AgentGuide -->|Semantic Search| Qdrant
    AgentGuide -->|Read| Postgres
    AgentSupport -->|Read/Write| Postgres
    AgentSupport -->|Call Tool| SheetMCP
    AgentNews -->|Call Tool| SheetMCP

    %% MCP
    SheetMCP -->|Append Rows| GoogleSheets

    classDef api fill:#2c3e50,stroke:#34495e,stroke-width:2px,color:#fff;
    classDef agent fill:#27ae60,stroke:#2ecc71,stroke-width:2px,color:#fff;
    classDef db fill:#c0392b,stroke:#e74c3c,stroke-width:2px,color:#fff;
    classDef mcp fill:#8e44ad,stroke:#9b59b6,stroke-width:2px,color:#fff;

    class EvoAPI,Gateway api;
    class AgentSupport,AgentGuide,AgentNews,Orchestrator agent;
    class Postgres,Qdrant,Redis db;
    class SheetMCP mcp;
```

---

## 2. Orchestrator Routing Flow
This demonstrates how a user's incoming message is classified and routed to the correct autonomous agent.

```mermaid
sequenceDiagram
    participant User as WhatsApp User
    participant Gateway as Gateway Service
    participant Orch as Orchestrator
    participant Router as LLM Router
    participant Agent as Specialized Agent (Guide/Support/News)

    User->>Gateway: Sends message (e.g., "Je veux m'inscrire")
    Gateway->>Orch: POST /api/v1/invoke {user_id, message}
    
    Orch->>Orch: Load user session state
    
    alt Session has active agent?
        Orch->>Agent: Forward directly to active agent
    else No active agent
        Orch->>Router: Classify intent
        Router-->>Orch: Intent detected (e.g., "newsletter")
        Orch->>Agent: Route to designated agent
    end
    
    Agent-->>Orch: Response (with requires_human flag)
    Orch->>Orch: Save session state
    Orch-->>Gateway: HTTP 200 {response, active_agent}
    Gateway->>User: Send WhatsApp Reply
```

---

## 3. Newsletter Agent State Machine (LangGraph)
This diagram illustrates the step-by-step logic the Newsletter Agent uses to gather information, ask for consent, and save data to Google Sheets via MCP.

```mermaid
stateDiagram-v2
    [*] --> ExtractInformation : User Message

    state ExtractInformation {
        direction LR
        Analyze --> ValidateFields
        ValidateFields --> CheckMissing
    }

    ExtractInformation --> RequestMissing : Missing Fields (Email, Name, CIN)
    RequestMissing --> [*] : Ask user for missing field

    ExtractInformation --> AwaitingConsent : All Fields Present
    AwaitingConsent --> [*] : Ask user for consent (Oui/Non)

    state ConsentDecision <<choice>>
    [*] --> ConsentDecision : User replies to Consent
    
    ConsentDecision --> Subscribed : Accepted
    ConsentDecision --> Cancelled : Refused
    ConsentDecision --> AwaitingConsent : Unclear

    Subscribed --> CallSheetMCP : Save to Google Sheets
    CallSheetMCP --> [*] : Success message

    Cancelled --> [*] : Cancellation message
```

---

## 4. Support Request Flow with MCP
This flow shows the integration between the Support agent and the `sheet-gmcp` server to persist data without direct database access.

```mermaid
sequenceDiagram
    participant User
    participant Support as Support Agent
    participant MCP as Sheet GMCP
    participant Google as Google Sheets API

    User->>Support: "J'ai un problème avec ma candidature"
    Support->>User: "Quel est votre nom, email, CIN ?"
    User->>Support: Provides details
    Support->>User: "Acceptez-vous d'enregistrer ces données ?"
    User->>Support: "Oui"
    
    Note over Support,MCP: Support Agent delegates persistence to MCP
    Support->>MCP: Call Tool: append_visitor_request<br/>{name, email, cin, intent, details}
    
    MCP->>Google: append_row([name, email, cin, intent, details])
    Google-->>MCP: Success
    MCP-->>Support: Tool execution successful
    
    Support->>User: "Votre demande a été enregistrée. Un humain va vous répondre."
```
