# 2.2 Flux de l'Agent Support & Intégration MCP

Ce diagramme de séquence illustre comment l'Agent Support utilise le Model Context Protocol (MCP) pour externaliser la persistance des données. Au lieu de se connecter directement à une base de données, l'Agent demande à un serveur MCP d'exécuter l'action sur Google Sheets.

> [!TIP]
> **Comment l'utiliser dans Eraser.io :**
> Importez ce code Mermaid directement dans Eraser ou donnez-le à l'IA d'Eraser pour qu'elle le transforme en vue architecturale détaillée.

```mermaid
sequenceDiagram
    actor User as WhatsApp User
    participant Support as Support Agent (LangGraph)
    participant LLM as Google Gemini
    participant MCP as Sheet-GMCP Server
    participant GSheets as Google Sheets API

    User->>Support: "J'ai un problème avec la plateforme, voici mes infos..."
    
    rect rgb(240, 248, 255)
        Note right of Support: Extraction et Consentement
        Support->>LLM: Extraction des entités (Nom, Email, etc.)
        LLM-->>Support: Données structurées (Pydantic Validation)
        Support->>User: "Acceptez-vous l'utilisation de vos données ?"
        User->>Support: "Oui, j'accepte"
    end
    
    rect rgb(245, 235, 255)
        Note right of Support: Phase MCP (Model Context Protocol)
        Support->>MCP: Call Tool: `append_visitor_request`<br/>(Données JSON)
        MCP->>GSheets: API Call: append_row(data)
        GSheets-->>MCP: HTTP 200 OK
        MCP-->>Support: Tool execution success
    end
    
    Support->>User: "Votre requête a été bien enregistrée."
```
