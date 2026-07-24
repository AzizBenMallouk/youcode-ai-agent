# Questions probables du jury et Réponses recommandées

Ce document regroupe les questions techniques et fonctionnelles les plus probables que le jury pourrait poser lors de la soutenance, accompagnées de réponses précises et professionnelles.

---

### 1. Pourquoi WhatsApp plutôt qu’une application web ?
**Réponse :** WhatsApp est le canal de communication le plus utilisé et le plus accessible au Maroc. Demander à un candidat de télécharger une application ou de se connecter à un site web ajoute de la friction. WhatsApp permet de joindre les candidats directement là où ils sont, avec un taux de lecture proche de 100%.

### 2. Pourquoi plusieurs agents plutôt qu’un seul ?
**Réponse :** Pour des raisons de fiabilité et de sécurité (principe du "Separation of Concerns"). Un seul LLM avec tous les outils et instructions serait confus ("Prompt Bloat"). En séparant le Support (qui a besoin d'outils d'extraction stricts) du Guide (qui a besoin du RAG), on réduit considérablement les risques d'hallucination et on garantit des flux prédictibles.

### 3. Pourquoi LangGraph ?
**Réponse :** Les frameworks classiques (comme LangChain ou LlamaIndex) sont souvent linéaires. LangGraph permet de créer un graphe cyclique avec des états. C'est essentiel pour interrompre l'exécution (attendre qu'un visiteur réponde sur WhatsApp le lendemain) et reprendre le flux là où il s'était arrêté sans perdre le contexte.

### 4. Pourquoi LangChain ?
**Réponse :** LangChain offre un écosystème riche pour manipuler les LLMs, standardiser les requêtes (indépendamment de si on utilise Gemini, Grok ou Ollama) et gérer les sorties structurées Pydantic avec la méthode `with_structured_output`.

### 5. Pourquoi utiliser un RAG ?
**Réponse :** Les modèles d'IA ne connaissent pas les règles internes de YouCode, ni les détails des campus ou les dates limites. Le RAG (Retrieval-Augmented Generation) force l'IA à sourcer ses réponses exclusivement à partir de nos propres documents internes mis à jour.

### 6. Comment éviter les hallucinations ?
**Réponse :** 
1. Par un "System Prompt" très restrictif qui ordonne au modèle de dire "Je ne sais pas" si l'info manque.
2. Par le découpage sémantique (Chunking) qui ne fournit que le contexte strictement nécessaire.
3. Par l'agent "Supervisor" qui isole les tâches de question-réponse du reste.

### 7. Pourquoi Qdrant ?
**Réponse :** Qdrant est une base de données vectorielle ultra-rapide, scalable, et qui s'intègre parfaitement avec LangChain. Elle permet des recherches par similarité cosinus avec une latence minimale, idéale pour un chatbot temps réel.

### 8. Pourquoi l’architecture parent–child pour le RAG ?
**Réponse :** Le "Parent-Child Retriever" est une technique avancée. Les "Child chunks" (petits morceaux) sont idéaux pour une recherche sémantique très précise (matching exact de la requête). Une fois le meilleur "Child" trouvé, on renvoie au LLM le "Parent" complet (le document entier) pour qu'il ait suffisamment de contexte pour formuler une réponse riche et nuancée.

### 9. Quelle différence entre le state et la persistance ?
**Réponse :** Le **State** (géré par SQLite localement) est la mémoire à court terme de la conversation : de quoi on parle, quelle question a été posée en dernier, quel brouillon est en cours. La **Persistance métier** (Google Sheets via MCP) est la mémoire à long terme et officielle : les rapports d'anomalie, les abonnements effectifs.

### 10. Pourquoi utiliser MCP (Model Context Protocol) ?
**Réponse :** MCP standardise la manière dont les LLMs accèdent aux ressources externes. Au lieu de coder l'API Google Sheets en dur dans les prompts de l'agent, le serveur MCP expose des outils (`append_row`, `read_sheet`). C'est plus sécurisé et agnostique : l'agent ne connaît pas la logique technique sous-jacente.

### 11. Pourquoi Google Sheets ?
**Réponse :** Pour permettre aux responsables d'admission non-techniques d'accéder aux données immédiatement sans avoir besoin d'apprendre un nouvel outil ou une nouvelle interface d'administration complexe. Cela permet un suivi immédiat.

### 12. Comment empêcher les doublons ?
**Réponse :** Le Support Agent utilise l'extraction structurée pour l'e-mail ou le numéro de téléphone. Le système vérifie l'existence de la demande en base locale avant de déclencher une nouvelle insertion MCP.

### 13. Comment protéger les données personnelles ?
**Réponse :** Nous appliquons la minimisation des données. L'agent Support ne demande que le strict nécessaire. De plus, aucune donnée métier n'est envoyée dans les logs publics, et nous utilisons des fournisseurs certifiés. L'étape de "Consentement explicite" garantit la conformité RGPD/CNDP avant toute écriture en base.

### 14. Comment valider le consentement ?
**Réponse :** Le flux s'arrête (node `support_missing` ou `newsletter_consent`). L'agent pose clairement la question. La réponse suivante du visiteur passe par une validation LLM (`classify_consent` via Pydantic) qui retourne un booléen. Si c'est "Non", les données du brouillon sont purgées.

### 15. Que se passe-t-il si Google Sheets est indisponible ?
**Réponse :** Grâce à notre architecture découplée avec SQLAlchemy, l'événement `after_insert` peut échouer silencieusement via MCP, mais la donnée transactionnelle est conservée dans notre base SQLite. Un système de "Retry" ou une tâche cron de synchronisation pourra rattraper les écritures échouées.

### 16. Que se passe-t-il si le LLM est indisponible ?
**Réponse :** FastAPI capte le timeout et renvoie un message statique : "Une erreur technique est survenue. Veuillez réessayer plus tard." Cela évite au visiteur d'attendre indéfiniment sans réponse.

### 17. Comment migrer vers PostgreSQL ?
**Réponse :** Étant donné que nous utilisons SQLAlchemy, la migration est triviale. Il suffit de changer l'URL de connexion dans le fichier `.env` (`DATABASE_URL=postgresql://...`) et de lancer les migrations Alembic. Le code de l'agent restera strictement identique.

### 18. Pourquoi conserver une validation humaine ?
**Réponse :** L'IA est un assistant, pas un décisionnaire. Pour des actions sensibles comme reporter une date de test qui impacte l'organisation d'un campus, l'IA fait 90% du travail (collecte, propositions, validation des disponibilités), mais le clic final "Approuver" appartient au responsable YouCode.

### 19. Comment tester la qualité des réponses ?
**Réponse :** Nous avons développé des scripts Python de test (ex: `test_multi_agent.py`) pour simuler des conversations. Nous pouvons y injecter un jeu de données standardisé pour vérifier que le Supervisor classe toujours bien les intentions.

### 20. Comment reprendre une conversation WhatsApp ?
**Réponse :** LangGraph utilise un `thread_id` (généré à partir du numéro de téléphone WhatsApp). À chaque message, le `Checkpointer` charge l'historique complet de ce `thread_id`. Le graphe reprend son exécution de manière transparente, même plusieurs jours après.
