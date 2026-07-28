# 3.2 Machine d'État (Agent Newsletter)

Ce diagramme d'état (State Machine) montre le flux de l'Agent Newsletter avec **LangGraph**. Il illustre comment le système extrait les préférences de la newsletter (S'abonner / Se désabonner), gère les cas d'erreur de validation (Pydantic), et pousse le résultat vers Google Sheets via MCP.

> [!TIP]
> **Comment l'utiliser dans Eraser.io :**
> Importez ce code Mermaid directement dans Eraser ou donnez-le à l'IA d'Eraser pour qu'elle le transforme en vue architecturale détaillée.

```mermaid
stateDiagram-v2
    [*] --> ExtractInformation : Nouveau Message (Input)

    state ExtractInformation {
        [*] --> CallLLM
        CallLLM --> ValidateSchema
        
        state ValidationCheck <<choice>>
        ValidateSchema --> ValidationCheck
        
        ValidationCheck --> ParseSuccess : Succès
        ValidationCheck --> ParseError : Erreur (Ex: length > max)
    }

    ExtractInformation --> TechnicalError : Si ParseError
    TechnicalError --> [*] : "Une erreur technique est survenue."

    ExtractInformation --> RequestMissingInformation : Si ParseSuccess mais champs manquants
    RequestMissingInformation --> [*] : Pose une question (Email ?, Nom ?, CIN ?)

    ExtractInformation --> AwaitingConsent : Si ParseSuccess et champs complets
    AwaitingConsent --> [*] : "Confirmez-vous que vous acceptez... (oui/non)"
    
    state ConsentDecision <<choice>>
    [*] --> ConsentDecision : Réponse de l'utilisateur
    
    ConsentDecision --> ProcessRequest : Accepté (oui)
    ConsentDecision --> Cancelled : Refusé (non)
    ConsentDecision --> AwaitingConsent : Incompréhensible
    
    Cancelled --> [*] : "Inscription annulée."

    ProcessRequest --> CallMCP : MCP tool `append_newsletter_subscription`
    CallMCP --> Completed : Stockage réussi
    Completed --> [*] : "Inscription validée."
```
