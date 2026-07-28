# 1.2 Container Diagram (Niveau 2)

Ce diagramme plonge à l'intérieur du système "YouCode AI Platform". Il montre les différents conteneurs (Microservices), la façon dont le trafic circule, et les bases de données attachées à chaque service.

> [!TIP]
> **Comment l'utiliser dans Eraser.io :**
> Importez ce code Mermaid directement dans Eraser ou donnez-le à l'IA d'Eraser pour qu'elle le transforme en vue architecturale détaillée.

```mermaid
graph TD
    %% Systèmes Externes
    EvoAPI[<b>Evolution API</b><br/><i>Système Externe</i>]
    GoogleSheets[<b>Google Sheets API</b><br/><i>Système Externe</i>]
    Gemini[<b>Google Gemini</b><br/><i>LLM Provider</i>]

    subgraph "YouCode AI Platform (Docker Compose)"
        %% Microservices de l'App
        Gateway(<b>Gateway</b><br/><i>FastAPI</i><br/>Webhook Receiver & Proxy)
        Orchestrator(<b>Orchestrator</b><br/><i>FastAPI + LangChain</i><br/>Session Manager & LLM Router)
        
        %% Agents
        subgraph "Agents de traitement (A2A Protocol)"
            AgentNews(<b>Newsletter Agent</b><br/><i>LangGraph</i>)
            AgentSupport(<b>Support Agent</b><br/><i>LangGraph</i>)
            AgentGuide(<b>Guide Agent</b><br/><i>LangGraph + RAG</i>)
        end
        
        %% Serveur MCP
        SheetMCP(<b>Sheet GMCP</b><br/><i>FastMCP Server</i><br/>Model Context Protocol)

        %% Bases de données
        Postgres[(<b>PostgreSQL</b><br/><i>Database</i><br/>Sessions, Logs, Instances)]
        Redis[(<b>Redis</b><br/><i>Cache / PubSub</i><br/>Sessions Evolution API)]
        Qdrant[(<b>Qdrant</b><br/><i>Vector Database</i><br/>Documents YouCode)]
    end

    %% Connexions externes entrant/sortant
    EvoAPI <-->|HTTP POST / Webhooks| Gateway
    Gateway -->|Invoke Request| Orchestrator
    
    %% Communication Orchestrateur -> Agents
    Orchestrator -->|HTTP JSON / Invoke| AgentNews
    Orchestrator -->|HTTP JSON / Invoke| AgentSupport
    Orchestrator -->|HTTP JSON / Invoke| AgentGuide

    %% Agent Dependencies
    AgentGuide -->|Semantic Search| Qdrant
    AgentSupport -->|Call MCP Tool| SheetMCP
    AgentNews -->|Call MCP Tool| SheetMCP
    
    %% Persistence
    SheetMCP -->|REST API| GoogleSheets
    Orchestrator -->|Read/Write State| Postgres
    EvoAPI -->|Cache| Redis
    EvoAPI -->|Data| Postgres

    %% Styles C4
    classDef container fill:#438dd5,stroke:#3c7fc0,color:#ffffff,stroke-width:2px
    classDef db fill:#c0392b,stroke:#e74c3c,color:#ffffff,stroke-width:2px
    classDef external fill:#999999,stroke:#6b6b6b,color:#ffffff,stroke-width:2px
    classDef mcp fill:#8e44ad,stroke:#9b59b6,color:#ffffff,stroke-width:2px

    class EvoAPI,GoogleSheets,Gemini external
    class Gateway,Orchestrator,AgentNews,AgentSupport,AgentGuide container
    class Postgres,Redis,Qdrant db
    class SheetMCP mcp
```
