# 1.3 Component Diagram (Niveau 3 - Zoom sur l'Orchestrateur)

Ce diagramme corrige l'architecture interne de **l'Orchestrateur**. Il explique comment les messages sont reçus par le contrôleur FastAPI, envoyés au graphe LangGraph de l'orchestrateur (Supervisor), puis relayés à l'agent final via le protocole A2A.

> [!TIP]
> **Comment l'utiliser dans Eraser.io :**
> Importez ce code Mermaid directement dans Eraser ou donnez-le à l'IA d'Eraser pour qu'elle le transforme en vue architecturale détaillée.

```mermaid
graph TD
    %% Entrées
    Gateway["Gateway Service"] -->|"HTTP POST<br/>/api/v1/invoke"| API["FastAPI Controller"]

    subgraph "Orchestrator Service"
        API -->|"1. ainvoke(state)"| LangGraph["LangGraph<br/>(Supervisor Graph)"]
        
        subgraph "LangGraph Logic"
            LangGraph --> Checkpointer["Postgres Checkpointer"]
            LangGraph --> LLMRouter["Supervisor LLM<br/>Semantic Classifier"]
        end
        
        LangGraph -->|"2. Returns Route"| API
        
        API -->|"3. A2A Client"| A2A["A2A HTTP Client"]
    end
    
    %% Base de données
    Postgres[("PostgreSQL<br/>Session Store")]
    Checkpointer <-->|"Save/Load<br/>Thread State"| Postgres

    %% Sorties vers les autres conteneurs (via A2A)
    A2A -->|"HTTP POST /api/v1/invoke"| NewsAPI["Newsletter Agent"]
    A2A -->|"HTTP POST /api/v1/invoke"| SupportAPI["Support Agent"]
    A2A -->|"HTTP POST /api/v1/invoke"| GuideAPI["Guide Agent"]
    
    %% Styles C4
    classDef container fill:#438dd5,stroke:#3c7fc0,color:#ffffff,stroke-width:2px
    classDef component fill:#85bbf0,stroke:#5b9dd9,color:#000000,stroke-width:2px
    classDef external fill:#999999,stroke:#6b6b6b,color:#ffffff,stroke-width:2px
    classDef db fill:#c0392b,stroke:#e74c3c,color:#ffffff,stroke-width:2px

    class Gateway,NewsAPI,SupportAPI,GuideAPI container
    class API,LangGraph,Checkpointer,LLMRouter,A2A component
    class Postgres db
```
