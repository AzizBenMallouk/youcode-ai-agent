# 3.1 Machine d'État (Agent Support)

Ce diagramme d'état (State Machine) explique le comportement de l'Agent Support propulsé par **LangGraph**. Il met en évidence le parcours cyclique de la conversation, de la collecte des informations manquantes, jusqu'à la demande de consentement et la proposition d'une nouvelle session de test (dans le cas d'un report).

> [!TIP]
> **Comment l'utiliser dans Eraser.io :**
> Importez ce code Mermaid directement dans Eraser ou donnez-le à l'IA d'Eraser pour qu'elle le transforme en vue architecturale détaillée.

```mermaid
stateDiagram-v2
    [*] --> ExtractInformation : Nouveau Message (Input)

    state ExtractInformation {
        [*] --> CallLLM
        CallLLM --> ValidateSchema
        ValidateSchema --> CheckMissingFields
    }

    ExtractInformation --> RequestMissingInformation : Si des champs obligatoires manquent
    RequestMissingInformation --> [*] : Pose une question à l'utilisateur

    ExtractInformation --> AwaitingConsent : Tous les champs sont remplis
    AwaitingConsent --> [*] : Demande explicitement "Oui" ou "Non"
    
    state ClassificationConsentement <<choice>>
    [*] --> ClassificationConsentement : Réponse de l'utilisateur
    
    ClassificationConsentement --> ProcessRequest : "Oui" (Accepté)
    ClassificationConsentement --> Cancelled : "Non" (Refusé)
    ClassificationConsentement --> AwaitingConsent : Incompréhensible
    
    Cancelled --> [*] : "Demande annulée."

    ProcessRequest --> CallMCP : Enregistre sur Google Sheets
    
    state CheckIntent <<choice>>
    CallMCP --> CheckIntent
    
    CheckIntent --> Completed : Demande standard (Support/Plainte)
    CheckIntent --> SessionProposal : Report de test (Test Reschedule)
    
    SessionProposal --> [*] : Propose une date "Le XX/XX/XXXX vous convient-il ?"
    
    state SessionDecision <<choice>>
    [*] --> SessionDecision : Réponse sur la date
    
    SessionDecision --> Completed : Accepté
    SessionDecision --> SearchAlternative : Refusé
    SessionDecision --> SessionProposal : Incompréhensible
    
    SearchAlternative --> SessionProposal : Propose une nouvelle date
    
    Completed --> [*] : "Demande traitée avec succès."
```
