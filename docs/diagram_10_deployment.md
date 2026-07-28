# 4.2 Diagramme de Déploiement (Infrastructure)

Ce diagramme décrit l'infrastructure physique du projet sur le serveur, telle que définie dans le fichier `compose.yaml`. Il montre les réseaux isolés, le mappage des ports, l'utilisation des volumes virtuels Docker, et surtout **toutes les dépendances correctes à la base Postgres** (utilisée par tous les agents comme Checkpointer).

> [!TIP]
> **Comment l'utiliser dans Eraser.io :**
> Importez ce code Mermaid directement dans Eraser ou donnez-le à l'IA d'Eraser pour qu'elle le transforme en vue architecturale détaillée.

```mermaid
graph TD
    %% Internet Edge
    Internet(("Internet / Web"))

    subgraph "Serveur Hôte (Docker Engine)"
        
        %% Mappage des Ports (Edge)
        Port8000["Port 8000<br/>Gateway"]
        Port8090["Port 8090<br/>Evo API"]
        
        Internet -->|"Webhooks WhatsApp"| Port8090
        Internet -->|"Webhooks Evo API"| Port8000

        subgraph "Réseau Virtuel: youcode-ai-agent_default"
            
            %% Microservices Python / FastAPI
            NodeGateway["youcode-gateway"]
            NodeOrchestrator["youcode-orchestrator"]
            NodeSheetMCP["youcode-sheet-gmcp"]
            
            %% Agents
            NodeSupport["youcode-support"]
            NodeNews["youcode-newsletter"]
            NodeGuide["youcode-guide"]
            
            %% Evo API
            NodeEvoAPI["youcode-evolution-api"]
            
            %% Bases de données
            NodeRedis[("youcode-redis")]
            NodePostgres[("youcode-postgres")]
            NodeQdrant[("youcode-qdrant")]
            
            %% Connexions API
            Port8000 --> NodeGateway
            Port8090 --> NodeEvoAPI
            
            NodeGateway <--> NodeOrchestrator
            NodeOrchestrator <--> NodeSupport
            NodeOrchestrator <--> NodeNews
            NodeOrchestrator <--> NodeGuide
            
            %% Connexions MCP
            NodeSupport --> NodeSheetMCP
            NodeNews --> NodeSheetMCP
            
            %% Connexions Base de Données (Toutes)
            NodeEvoAPI <--> NodeRedis
            NodeEvoAPI <--> NodePostgres
            NodeGuide <--> NodeQdrant
            NodeGuide <--> NodePostgres
            NodeOrchestrator <--> NodePostgres
            NodeSupport <--> NodePostgres
            NodeNews <--> NodePostgres
        end
        
        %% Volumes Persistants
        subgraph "Volumes Docker (Stockage Persistant)"
            VolQdrant[["qdrant_data"]]
            VolPostgres[["postgres_data"]]
            VolEvo[["evolution_instances"]]
            VolCreds[["./youcode-*.json<br/>(Bind Mount)"]]
        end
        
        %% Mapping Volumes
        NodeQdrant -.-> VolQdrant
        NodePostgres -.-> VolPostgres
        NodeEvoAPI -.-> VolEvo
        NodeSheetMCP -.-> VolCreds
    end
    
    %% Styles
    classDef edge fill:#f39c12,stroke:#e67e22,color:#ffffff,stroke-width:2px
    classDef docker fill:#3498db,stroke:#2980b9,color:#ffffff,stroke-width:2px
    classDef db fill:#c0392b,stroke:#e74c3c,color:#ffffff,stroke-width:2px
    classDef vol fill:#95a5a6,stroke:#7f8c8d,color:#ffffff,stroke-width:2px

    class Port8000,Port8090 edge
    class NodeGateway,NodeOrchestrator,NodeSheetMCP,NodeSupport,NodeNews,NodeGuide,NodeEvoAPI docker
    class NodeRedis,NodePostgres,NodeQdrant db
    class VolQdrant,VolPostgres,VolEvo,VolCreds vol
```
