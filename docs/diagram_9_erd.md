# 4.1 Modèle de Données (ERD)

Ce diagramme Entité-Association (Entity-Relationship Diagram) illustre la persistance des données. 
Avec le passage au Model Context Protocol (MCP), les requêtes utilisateurs ne sont plus stockées dans PostgreSQL, mais directement ajoutées en tant que lignes dans **Google Sheets**. La base de données PostgreSQL reste utilisée par l'API Evolution pour ses propres instances.

> [!TIP]
> **Comment l'utiliser dans Eraser.io :**
> Importez ce code Mermaid directement dans Eraser ou donnez-le à l'IA d'Eraser pour qu'elle le transforme en vue architecturale détaillée.

```mermaid
erDiagram
    %% Google Sheets Entities (Gérées via Sheet-GMCP)
    VISITOR_REQUESTS {
        string user_id "WhatsApp JID"
        string first_name "Prénom"
        string last_name "Nom"
        string email "Adresse email"
        string cin "Numéro CIN"
        string campus "Safi, Youssoufia, Nador"
        string intent "Type de requête (ex: support)"
        string details "Description du problème"
    }

    NEWSLETTER_SUBSCRIPTIONS {
        string email "Adresse email"
        string status "subscribed / unsubscribed"
    }

    %% PostgreSQL Entities (Gérées par Evolution API)
    EVOLUTION_INSTANCES {
        uuid id PK
        string instanceName "Ex: youcode-ai"
        string token "Auth Token"
        string integration "WHATSAPP-BAILEYS"
        datetime created_at
    }

    %% Relations (Conceptuelles)
    EVOLUTION_INSTANCES ||--o{ VISITOR_REQUESTS : "Reçoit les messages de"
```
