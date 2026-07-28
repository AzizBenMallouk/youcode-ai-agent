# 1.1 Context Diagram (Niveau 1)

Ce premier diagramme montre le système "YouCode AI Platform" au centre, avec les acteurs et les systèmes externes qui l'entourent. C'est la vue la plus haute pour comprendre les frontières du système.

> [!TIP]
> **Comment l'utiliser dans Eraser.io :**
> Vous pouvez copier le code Mermaid ci-dessous et l'importer directement dans Eraser via l'option **"Import Mermaid"**, ou bien le copier-coller dans le prompt de l'IA d'Eraser en demandant *"Génère une architecture basée sur ce code"*.

```mermaid
graph TD
    %% Acteurs
    Candidate((Candidat /<br/>Étudiant))
    Admin((Administrateur<br/>YouCode))

    %% Le système principal
    System[<b>YouCode AI Platform</b><br/><i>Système Logiciel</i><br/>Gère les requêtes d'assistance, guide<br/>les utilisateurs et gère les newsletters<br/>de manière automatisée via IA.]

    %% Systèmes externes
    WhatsApp[<b>WhatsApp</b><br/><i>Système Externe</i><br/>Interface de communication]
    EvolutionAPI[<b>Evolution API</b><br/><i>Système Externe</i><br/>Pont de messagerie WhatsApp]
    LLM[<b>Google Gemini (LLM)</b><br/><i>Système Externe</i><br/>Moteur d'intelligence artificielle]
    GoogleSheets[<b>Google Sheets</b><br/><i>Système Externe</i><br/>Stockage persistant des requêtes<br/>et inscriptions]

    %% Relations
    Candidate -->|Pose des questions et<br/>envoie des requêtes via| WhatsApp
    Admin -->|Consulte les données via| GoogleSheets
    
    WhatsApp <-->|Webhooks & API| EvolutionAPI
    EvolutionAPI <-->|Route les messages| System
    
    System <-->|Envoie des requêtes<br/>de raisonnement| LLM
    System -->|Sauvegarde les<br/>données via MCP| GoogleSheets

    %% Styles pour différencier les éléments (Norme C4)
    classDef person fill:#08427b,stroke:#052e56,color:#ffffff,stroke-width:2px
    classDef system fill:#1168bd,stroke:#0b4884,color:#ffffff,stroke-width:2px
    classDef external fill:#999999,stroke:#6b6b6b,color:#ffffff,stroke-width:2px

    class Candidate,Admin person
    class System system
    class WhatsApp,EvolutionAPI,LLM,GoogleSheets external
```
