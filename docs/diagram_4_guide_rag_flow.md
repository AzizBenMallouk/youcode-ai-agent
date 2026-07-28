# 2.1 Flux de l'Agent Guide (RAG)

Ce diagramme de séquence illustre le fonctionnement du flux RAG (Retrieval-Augmented Generation) utilisé par le **Guide Agent**. Il montre comment les questions des utilisateurs sont enrichies par le contexte des documents internes de YouCode stockés dans la base vectorielle.

> [!TIP]
> **Comment l'utiliser dans Eraser.io :**
> Importez ce code Mermaid directement dans Eraser ou donnez-le à l'IA d'Eraser pour qu'elle le transforme en vue architecturale détaillée.

```mermaid
sequenceDiagram
    actor User as Utilisateur
    participant Orch as Orchestrator
    participant Guide as Guide Agent
    participant Embed as Modèle d'Embedding
    participant Vector as Qdrant (Base Vectorielle)
    participant Rerank as Re-ranker (Cross-Encoder)
    participant LLM as Google Gemini

    User->>Orch: "Quelles sont les conditions d'admission ?"
    Orch->>Guide: Invoke Request
    
    rect rgb(240, 248, 255)
        Note right of Guide: Phase 1 : Recherche (Retrieval)
        Guide->>Embed: Calcule les vecteurs de la question
        Embed-->>Guide: Vector Embeddings
        Guide->>Vector: Recherche de similarité cosinus (Top K)
        Vector-->>Guide: Documents bruts potentiellement pertinents
    end
    
    rect rgb(245, 245, 245)
        Note right of Guide: Phase 2 : Re-Ranking (Optionnel / Avancé)
        Guide->>Rerank: Évalue la pertinence (Question + Docs)
        Rerank-->>Guide: Documents triés par pertinence stricte
    end
    
    rect rgb(255, 245, 238)
        Note right of Guide: Phase 3 : Génération (Augmented Generation)
        Guide->>LLM: Prompt enrichi avec le Contexte + Question
        LLM-->>Guide: Réponse sourcée et précise
    end
    
    Guide-->>Orch: HTTP 200 { response }
    Orch-->>User: "Les conditions d'admission sont..."
```
