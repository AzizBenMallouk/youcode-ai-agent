# 2.3 Gestion du Webhook & File d'attente (Gateway)

Ce diagramme de séquence montre le rôle du Gateway. Son but est d'intercepter les requêtes WhatsApp, de filtrer les bruits de fond (les messages envoyés par nous-mêmes), et de lancer les appels à l'Orchestrateur de manière asynchrone (Background Tasks) pour retourner rapidement un statut 200 OK à Evolution API et éviter les timeouts.

> [!TIP]
> **Comment l'utiliser dans Eraser.io :**
> Importez ce code Mermaid directement dans Eraser ou donnez-le à l'IA d'Eraser pour qu'elle le transforme en vue architecturale détaillée.

```mermaid
sequenceDiagram
    participant WhatsApp
    participant EvoAPI as Evolution API
    participant Gateway as Gateway Service
    participant Orch as Orchestrator
    
    WhatsApp->>EvoAPI: User sends message
    EvoAPI->>Gateway: POST /api/v1/whatsapp/webhook<br/>(event: messages.upsert)
    
    Gateway->>Gateway: Filter: event == messages.upsert ?
    Gateway->>Gateway: Filter: fromMe == False ?
    
    alt Filtre échoué (ex: ack, fromMe)
        Gateway-->>EvoAPI: HTTP 200 { status: "ignored" }
    else Message valide
        Gateway->>Gateway: FastAPI Background Task<br/>(process_and_reply)
        Gateway-->>EvoAPI: HTTP 200 { status: "accepted" }
        
        Note right of Gateway: Asynchronous execution starts here
        Gateway->>Orch: POST /api/v1/invoke
        Orch-->>Gateway: Result (Answer)
        
        Gateway->>EvoAPI: POST /message/sendText<br/>(Réponse au User)
        EvoAPI->>WhatsApp: Envoie message
    end
```
