# Architecture Globale : YouCode AI Platform

Ces diagrammes expliquent le cycle de vie complet d'un message, avec des vues détaillées du fonctionnement interne et des interactions de **chaque agent**.

---

## 1. Flux Principal et Communication (RabbitMQ)
*Le cycle de vie complet d'un message, numéroté étape par étape.*

```mermaid
graph TD
    %% Utilisateurs et Interfaces
    UserWA((Utilisateur\nWhatsApp))
    UserDiscord((Utilisateur\nDiscord))
    EvoAPI[Evolution API]
    DiscordAPI[API Discord]

    %% Gateways
    WA_Gateway[WhatsApp Gateway]
    Discord_Gateway[Discord Gateway]

    %% RabbitMQ Queues
    Q_Incoming[(Queue:\nincoming_messages)]
    Q_Outbound[(Queue:\noutbound_messages)]
    
    Q_Guide[(Queue: guide_requests)]
    Q_Support[(Queue: support_requests)]
    Q_News[(Queue: newsletter_requests)]
    Q_Admin[(Queue: admin_requests)]

    %% Orchestrator
    Orchestrator{Orchestrateur\nSuperviseur LLM}
    Guardrail[Guardrail Service\n(Profanity + Qdrant)]

    %% Agents (Consommateurs)
    AgentGuide[Agent Guide]
    AgentSupport[Agent Support]
    AgentNews[Agent Newsletter]
    AgentAdmin[Agent Admin]

    %% Flux
    UserWA -->|(1) Message| EvoAPI
    UserDiscord -->|(1) Message| DiscordAPI
    
    EvoAPI -->|(2) Webhook| WA_Gateway
    DiscordAPI -->|(2) Websocket| Discord_Gateway

    WA_Gateway -->|(3) Publie| Q_Incoming
    Discord_Gateway -->|(3) Publie| Q_Incoming
    
    Q_Incoming -->|(4) Consomme| Orchestrator
    Orchestrator <-->|(5) Vérifie Sécurité| Guardrail

    Orchestrator -->|(6) Route: Intent| Q_Guide
    Orchestrator -->|(6) Route: Intent| Q_Support
    Orchestrator -->|(6) Route: Intent| Q_News
    Orchestrator -->|(6) Route: Intent| Q_Admin

    Q_Guide -->|(7) Consomme| AgentGuide
    Q_Support -->|(7) Consomme| AgentSupport
    Q_News -->|(7) Consomme| AgentNews
    Q_Admin -->|(7) Consomme| AgentAdmin

    AgentGuide -->|(8) Publie Réponse| Q_Outbound
    AgentSupport -->|(8) Publie Réponse| Q_Outbound
    AgentNews -->|(8) Publie Réponse| Q_Outbound
    AgentAdmin -->|(8) Publie Réponse| Q_Outbound

    Q_Outbound -->|(9) Consomme (source=whatsapp)| WA_Gateway
    Q_Outbound -->|(9) Consomme (source=discord)| Discord_Gateway

    WA_Gateway -->|(10) POST Reply| EvoAPI
    Discord_Gateway -->|(10) API Call| DiscordAPI
    
    EvoAPI -->|(11) Message| UserWA
    DiscordAPI -->|(11) Message| UserDiscord
```

---

## 2. Graphes Cognitifs par Agent (LangGraph)

Chaque agent possède sa propre logique métier. Voici comment fonctionne la boucle `ReAct` (ou le State Machine) de chacun d'eux.

### A. Agent Guide (RAG & Info)
```mermaid
stateDiagram-v2
    direction TB
    [*] --> LoadState: Réception Message
    LoadState --> AgentNode: Inject System Prompt
    
    state "LLM Décision (Guide)" as AgentNode
    state "Tools" as ToolsNode {
        state "search_youcode_knowledge" as RAG
        state "get_registration_status" as API
    }

    AgentNode --> RAG: Demande info générale
    AgentNode --> API: Demande statut d'inscription
    ToolsNode --> AgentNode: tool_results
    
    AgentNode --> SaveState: Génération réponse texte
    SaveState --> [*]: Envoi vers Outbound
```

### B. Agent Support (Prise de Rendez-vous / Dépannage)
```mermaid
stateDiagram-v2
    direction TB
    [*] --> ExtractInfo: Réception Message
    
    state "Extraction d'Entités" as ExtractInfo
    state "Validation" as Validate
    state "Formulation Question" as AskQuestion
    state "Action: send_rescheduling_email" as ActionEmail

    ExtractInfo --> Validate: Extrait (Date, Nom, Motif)
    Validate --> AskQuestion: Si infos manquantes
    Validate --> ActionEmail: Si toutes infos valides
    
    AskQuestion --> SaveState
    ActionEmail --> SaveState: MCP Email appelé
    SaveState --> [*]: Envoi vers Outbound
```

### C. Agent Newsletter (Collecte d'Abonnés)
```mermaid
stateDiagram-v2
    direction TB
    [*] --> AnalyzeIntent
    
    state "Analyse (S'abonner / Se désabonner)" as AnalyzeIntent
    state "Validation Email" as ValidateEmail
    state "Demande d'Email" as AskEmail
    state "Confirmer Inscription" as Confirm

    AnalyzeIntent --> ValidateEmail: Intention d'inscription détectée
    ValidateEmail --> AskEmail: Email manquant ou invalide
    ValidateEmail --> Confirm: Email valide trouvé
    
    AskEmail --> SaveState
    Confirm --> SaveState: Ajoute à la liste des abonnés
    SaveState --> [*]
```

### D. Agent Admin (Gestion & Reporting via MCP)
```mermaid
stateDiagram-v2
    direction TB
    [*] --> AgentNode
    
    state "LLM Décision (Admin)" as AgentNode
    state "Tools (MCP via Client)" as ToolsNode {
        state "get_visitor_requests" as GetReq
        state "generate_report_via_mcp" as SheetMCP
    }

    AgentNode --> GetReq: Demande de statistiques
    AgentNode --> SheetMCP: Demande création de rapport
    ToolsNode --> AgentNode: tool_results
    
    AgentNode --> SaveState
    SaveState --> [*]
```

---

## 3. Séquences de Communication et d'Outils (Interactions)

Voici comment chaque agent interagit concrètement avec ses outils, APIs ou serveurs MCP.

### A. Séquence : Agent Guide
L'Agent Guide utilise des outils internes (non-MCP).

```mermaid
sequenceDiagram
    participant User as Utilisateur
    participant Orchestrator as Orchestrateur
    participant GuideAgent as Agent Guide
    participant Qdrant as Qdrant (Base Vectorielle)
    participant FakeAPI as Fake Registration API

    User->>Orchestrator: "Comment s'inscrire et est-ce ouvert ?"
    Orchestrator->>GuideAgent: Message routé
    
    GuideAgent->>Qdrant: tool: search_youcode_knowledge("procédure inscription")
    Qdrant-->>GuideAgent: tool_result: Docs officiels
    
    GuideAgent->>FakeAPI: tool: get_registration_status()
    FakeAPI-->>GuideAgent: tool_result: {"status": "open"}
    
    GuideAgent->>User: "Voici comment s'inscrire... Et oui, c'est ouvert !"
```

### B. Séquence : Agent Support
L'Agent Support extrait des entités et déclenche un envoi d'email via un serveur MCP externe.

```mermaid
sequenceDiagram
    participant User as Utilisateur
    participant Orchestrator as Orchestrateur
    participant SupportAgent as Agent Support
    participant EmailMCP as Email MCP Server (SMTP)

    User->>Orchestrator: "Je veux reporter mon test à demain."
    Orchestrator->>SupportAgent: Message routé
    
    SupportAgent->>SupportAgent: Extrait "demain" (manque email/motif)
    SupportAgent->>User: "Quel est votre email et motif ?"
    
    User->>Orchestrator: "C'est jean@test.com pour cause maladie."
    Orchestrator->>SupportAgent: Message routé
    
    SupportAgent->>SupportAgent: Validation: Infos complètes
    SupportAgent->>EmailMCP: Client HTTP SSE: call_tool("send_email")
    EmailMCP-->>SupportAgent: "Email envoyé"
    
    SupportAgent->>User: "Parfait, la confirmation a été envoyée par email."
```

### C. Séquence : Agent Newsletter
L'Agent Newsletter est principalement conversationnel et gère un état interne.

```mermaid
sequenceDiagram
    participant User as Utilisateur
    participant Orchestrator as Orchestrateur
    participant NewsAgent as Agent Newsletter
    participant DB as Postgres (Checkpointer)

    User->>Orchestrator: "Je veux m'abonner à la newsletter."
    Orchestrator->>NewsAgent: Message routé
    
    NewsAgent->>NewsAgent: Analyse intent = S'abonner
    NewsAgent->>DB: Vérifie si email déjà fourni
    NewsAgent->>User: "Merci ! Quel est votre adresse email ?"
    
    User->>Orchestrator: "mon.email@gmail.com"
    Orchestrator->>NewsAgent: Message routé
    
    NewsAgent->>NewsAgent: ValidateEmail("mon.email@gmail.com")
    NewsAgent->>DB: Sauvegarde {"subscribed": true, "email": "mon.email@gmail.com"}
    NewsAgent->>User: "Vous êtes bien inscrit à notre newsletter."
```

### D. Séquence : Agent Admin
L'Agent Admin interagit avec le monde extérieur exclusivement via des serveurs MCP (Model Context Protocol).

```mermaid
sequenceDiagram
    participant Admin as Administrateur
    participant Orchestrator as Orchestrateur
    participant AdminAgent as Agent Admin
    participant DBAPI as Base de données / Cache
    participant SheetMCP as Sheet GMCP Server

    Admin->>Orchestrator: "Génère le rapport des visiteurs d'aujourd'hui."
    Orchestrator->>AdminAgent: Message routé
    
    AdminAgent->>DBAPI: tool: get_visitor_requests()
    DBAPI-->>AdminAgent: tool_result: [{"name": "Ali", "intent": "inscription"}]
    
    AdminAgent->>SheetMCP: Client HTTP SSE: call_tool("generate_admin_report", data)
    SheetMCP-->>AdminAgent: tool_result: "Sheet URL: https://docs.google.com/..."
    
    AdminAgent->>Admin: "Le rapport a été généré avec succès. Voici le lien."
```
