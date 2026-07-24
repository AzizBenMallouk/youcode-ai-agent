# Architecture Analysis: YouCode AI Platform

## 1. Composants détectés
- **FastAPI** : Sert de webhook d'entrée (WhatsApp) et d'API backend (routes `/api/v1/chat`, `/api/v1/support-requests`).
- **WhatsApp Web (Puppeteer)** : Un client Node.js/Puppeteer (`apps/whatsapp-bot`) qui scanne le QR code et interagit avec l'API FastAPI locale.
- **LangGraph** : Orchestrateur multi-agent qui gère le graphe de la conversation.
- **Qdrant** : Base de données vectorielle utilisée pour le RAG (Retrieval-Augmented Generation).
- **SQLite / SQLAlchemy** : Base de données relationnelle locale utilisée comme cache transactionnel et source de vérité applicative (modèles `ConsentGrantTable`, `KnowledgeGapTable`, `NewsletterSubscriptionTable`, `VisitorRequestTable`).
- **Google Sheets (MCP)** : Serveur MCP externe utilisé via des écouteurs d'événements SQLAlchemy (`after_insert`, `after_update`) pour synchroniser les données métier en temps réel avec un tableur Google Sheets (fonctionnant comme une base de suivi métier).
- **Gemini / Grok / Ollama** : Fournisseurs LLM intégrés.

## 2. Agents détectés
- **Supervisor Agent** : Détecte l'intention du visiteur et achemine (route) la requête vers le sous-agent approprié ou maintient la conversation dans le flux courant.
- **Guide Agent** : Spécialisé dans l'information institutionnelle. Utilise le RAG avec Qdrant pour répondre aux questions en s'appuyant uniquement sur les documents de YouCode.
- **Support Agent** : Gère les demandes des candidats (ex: report de test). Il extrait les informations structurées, vérifie les valeurs manquantes, demande un consentement, puis "traite" la requête.
- **Newsletter Agent** : Gère l'abonnement aux actualités. Il extrait les préférences, demande le consentement et enregistre l'abonnement.
- **Guardrails Agent** : *Incomplet/Pré-implémenté*. Node prévu pour valider les sorties avant l'envoi, mais non totalement branché ou utilisé dans tous les flux.

## 3. Outils (Tools) détectés
- **RAG Retriever** : Outil parent-child retriever qui découpe et indexe les documents officiels. Utilisé par le Guide Agent.
- **Extraction Tools** : Prompts structurés Pydantic (`with_structured_output`) pour extraire les entités des conversations pour le Support et la Newsletter.
- **MCP Google Sheets** : Un serveur FastMCP (`apps/api/src/youcode_ai/infrastructure/mcp/google_sheets_server.py`) qui expose les outils `append_row` et `read_sheet`. Le client MCP (`mcp_client.py`) est instancié au démarrage de FastAPI et appelé via des écouteurs d'événements (Event Listeners SQLAlchemy dans `events.py`).

## 4. Workflows (LangGraph) détectés
- **Routage Principal** : `route_graph_entry` (Supervisor)
- **Support Workflow** : Collecte (`support_extract`), Consentement (`support_consent`), Traitement (`support_process`), Propositions de Session (`support_session_decision`, `support_confirm_session`, `support_alternative`).
- **Newsletter Workflow** : Extraction (`newsletter_extract`), Consentement (`newsletter_consent`), Traitement (`newsletter_process`).
- **Guide Workflow** : Génération de la réponse via le graphe `answer_question`.

## 5. Endpoints détectés
- `POST /api/v1/chat` : Interface pour recevoir les messages (utilisée par le bot WhatsApp).
- `GET /health` : Endpoint de santé.
- `GET /api/v1/support-requests` : Interface pour lister/gérer les demandes de support.

## 6. Fonctionnalités Opérationnelles
- Scrapping / Connexion WhatsApp Web via Puppeteer.
- Orchestration LangGraph multi-agents fonctionnelle.
- RAG (Parent/Child chunking avec Qdrant) actif.
- Extraction d'entités avec structuration Pydantic (Newsletter / Support).
- Synchronisation asynchrone des bases de données SQL locales vers Google Sheets via MCP.
- Persistance locale en base relationnelle avec historique.

## 7. Fonctionnalités Incomplètes ou Partielles
- **Guardrails Agent** : Configuré mais son intégration dans le workflow principal semble rudimentaire.
- **Interface d'administration (UI)** : Les routes d'API admin existent (`support-requests`), mais l'interface front-end web (Next.js/React) n'est pas implémentée. Google Sheets joue actuellement le rôle de Dashboard Admin.
- **Intégrations API Externes (Test Sessions)** : L'API de sessions de test externe est simulée ou partiellement stubbée (interfaces définies mais le backend de YouCode Admission n'est pas réellement connecté).

## 8. Perspectives d'évolution
- Remplacement du Dashboard Google Sheets par un Dashboard Administrateur complet.
- Finalisation de l'Agent de Guardrails pour une modération proactive.
- Migration de SQLite vers PostgreSQL pour un déploiement cloud natif.
- Connexion réelle à l'ERP / SIS de YouCode (Système d'Information Scolaire) pour valider directement les reports de tests et sessions.
