# Codebase Review & Refactoring Documentation

## Task 1: Core & Shared Components (`shared/`)

### 1. Structure et Composants Analysés
Le dossier `shared/` contient l'architecture hexagonale / DDD partagée entre tous les microservices.
- **`core/`** : Gestion centralisée de la configuration via `pydantic-settings` (`config.py`) et instanciation des LLMs/Embeddings (`llm.py`).
- **`domain/`** : Énumérations (langues, status, intentions) et exceptions métiers.
- **`infrastructure/database/`** : Définition de l'ORM SQLAlchemy (Postgres) avec des tables comme `visitor_requests` et `newsletter_subscriptions`. Contient également un checkpointer pour LangGraph (`checkpointer.py`).
- **`infrastructure/mcp/`** : Serveur FastMCP pour interagir avec Google Sheets (`google_sheets_server.py`).
- **`mcp/`** : Client asynchrone universel pour dialoguer avec d'autres agents via le protocole MCP sur HTTP (`client.py`).
- **`messaging/`** : Client robuste RabbitMQ basé sur `aio_pika` pour les appels RPC inter-services (`broker.py`).
- **`rag/`** : Système de retrieval "Small-to-Big" avec Qdrant et `Flashrank` (`retriever.py`).

### 2. Améliorations Apportées (Fixes & Cleanups)
- **Nettoyage de `config.py` et `llm.py`** : 
  - Suppression de configurations mortes relatives à *Grok*.
  - Suppression des fournisseurs directs (Gemini/Ollama) pour le chat, puisque l'architecture utilise désormais exclusivement *LiteLLM* comme proxy central.
  - Suppression du hack `DummyEmbeddings`. Si l'API de vectorisation manque, l'application plantera explicitement au lieu de retourner des résultats silencieusement faux.
- **Analyse et suppression de la dette technique (MCP & BDD)** :
  - Le hook de base de données (`events.py`) et son faux client (`sheets_client.py`) qui faisaient un appel synchrone HTTP pour simuler le MCP ont été **totalement supprimés**. La base de données est désormais correctement découplée et ne dépend plus d'un outil destiné aux LLMs.

### 3. Conclusion de la Task 1
Le socle applicatif est robuste. L'utilisation de Pydantic pour la validation et de `aio_pika` pour RabbitMQ est respectueuse des bonnes pratiques modernes en Python (FastAPI/asyncio). Le code est prêt pour servir de base aux agents métiers.

## Task 2: API Gateway (`services/gateway/`)

### 1. Analyse et Flux de Messagerie
Le service Gateway est extrêmement léger (sans base de données ni LLM) et sert de pont entre WhatsApp et le système.
- **Provider WhatsApp** : Le code utilise exclusivement l'API *Evolution API* (et non Twilio).
- **Webhooks (`/api/v1/webhook/whatsapp`)** : Il reçoit les événements `messages.upsert` entrants.
- **Envoi de messages** : Il écoute la queue RabbitMQ `whatsapp_outbound` pour relayer les réponses de l'IA vers WhatsApp (centralisant ainsi toute la logique externe).
- **Sécurité** : Il implémente un filtrage strict par liste blanche de numéros et vérifie le `WEBHOOK_SECRET`.
- **Publication RabbitMQ** : Les messages valides sont publiés de façon asynchrone dans la queue `whatsapp_messages` avec le mode `PERSISTENT`.

### 2. Nettoyage du code obsolète
L'API Gateway est parfaitement propre. La faille de sécurité du webhook a été corrigée. Le front-end minimaliste intégré (`/qr`) permet l'appairage rapide du bot WhatsApp.

## Task 3: Orchestrator (`services/orchestrator/`)

### 1. Analyse et Architecture
L'Orchestrateur est le chef d'orchestre du système. Il consomme les messages de `whatsapp_messages` (RabbitMQ) et utilise un graphe (LangGraph) pour décider à quel agent déléguer la tâche.
- **Découplage WhatsApp** : L'Orchestrateur a été refactorisé. Il ne communique plus directement avec Evolution API. Une fois la réponse de l'agent obtenue (via RPC), l'Orchestrateur publie le résultat dans la queue `whatsapp_outbound` pour que la Gateway s'en charge. Cela respecte les principes microservices (Single Responsibility).
- **Graphe LangGraph** : Le graphe est composé de deux étapes principales :
  1. `guardrail` : Intercepte le message entrant pour s'assurer qu'il est sans danger. Si c'est un prompt injection ou un message offensant, la requête est bloquée net.
  2. `supervisor` : Si le message est sûr, le superviseur l'analyse et choisit vers quel agent l'envoyer (`guide`, `support`, `newsletter`, `admin`), ou s'il est "hors contexte" (out of scope).
- **Communication RPC** : L'Orchestrateur utilise le pattern RabbitMQ RPC (`resilient_rpc_call`). L'appel est asynchrone mais bloquant (attente d'une réponse de l'agent), avec un système de timeout (120s) empêchant le graphe de planter si un agent est indisponible.
- **Mémoire LangGraph** : L'état des conversations (Checkpointer) est stocké de manière persistante sur PostgreSQL (`AsyncPostgresSaver`), ce qui permet au système de se souvenir du contexte de chaque numéro de téléphone.

## Task 4: Newsletter Agent (`services/newsletter/`)

### 1. Analyse et Architecture
Contrairement à un agent générique, l'Agent Newsletter est conçu de manière **déterministe** et **hautement sécurisée**. Il utilise la puissance de LangGraph non pas pour "réfléchir librement", mais comme une véritable "State Machine" (Machine à États) pour collecter des informations précises (Nom, Email, Action, Campus, Sujets).

- **Extraction Structurée (Pydantic)** : Plutôt que de demander au LLM de générer du texte libre, le fichier `extractor.py` force le LLM (via `with_structured_output`) à remplir un modèle Pydantic précis.
- **Brouillon (Draft) progressif** : À chaque itération, l'agent fusionne intelligemment les nouvelles informations avec celles déjà collectées (`_merge_with_draft`).
- **Validation stricte** : Le module `validator.py` valide formellement les emails (via la librairie `email_validator`) et vérifie qu'aucun champ obligatoire ne manque avant de demander le consentement final.
- **Base de données** : L'enregistrement se fait directement dans PostgreSQL.

### 2. Nettoyage du code
Le code est très propre et optimisé. Les appels RPC RabbitMQ (via `main.py`) et l'endpoint de debug HTTP sont correctement implémentés. Les prompts (`prompt.py`) sont clairs et limités à l'extraction.

## Task 5: Support Agent (`services/support/`)

### 1. Analyse et Création de Tickets
Tout comme l'Agent Newsletter, l'Agent Support est une State Machine (LangGraph) déterministe basée sur l'extraction Pydantic (`SupportInformationExtraction`).
- Il identifie l'intention parmi plusieurs types de requêtes (`login_problem`, `test_reschedule`, etc.).
- Il boucle intelligemment pour réclamer les informations manquantes une par une (via le dictionnaire de questions `QUESTION_BY_FIELD`).

### 2. Logique de Reprogrammation (Rescheduling)
La logique de report de test est particulièrement avancée :
- Si la demande est `test_reschedule`, l'agent propose une nouvelle date.
- Si le candidat refuse, la session est ajoutée à une liste noire (`rejected_session_ids`) et l'agent cherche une alternative (`search_alternative_session`).
- Si le candidat accepte, l'agent utilise le client MCP (`shared.mcp.client.call_agent_tool`) pour contacter le serveur `email-mcp` et envoyer un email de confirmation de report de test de manière asynchrone.

### 3. Validation MCP & Fallback
C'est le premier agent à intégrer pleinement la nouvelle architecture MCP (`call_agent_tool("send_rescheduling_email")`). La création basique du ticket se fait sur PostgreSQL (`VisitorRequest`). Les scénarios d'erreurs et de refus sont bien gérés (fallback vers un humain ou annulation de la requête).

## Task 6: Guide Agent - RAG (`services/guide/`)

### 1. Intégration RAG Avancée avec Qdrant
L'agent Guide est un agent *ReAct* complet implémenté avec `langchain.agents`. L'intégration de la base de données vectorielle (Qdrant) est extrêmement bien construite via le module `shared.rag.retriever` :
- **Parent-Child Retrieval (Small-to-Big)** : Les embeddings sont calculés sur de petits morceaux de texte (chunks/children) pour une recherche sémantique précise, mais l'agent reçoit le document parent complet pour maximiser le contexte.
- **Reranking** : Utilisation optionnelle de `FlashrankRerank` pour réordonner les résultats et améliorer la pertinence.

### 2. Outils (Tools)
L'agent possède deux outils principaux :
- `search_youcode_knowledge` : Interroge Qdrant pour les informations stables (programmes, campus, etc.).
- `get_registration_status` : Interroge dynamiquement l'API d'inscription. La consigne du prompt indique clairement que cette API a la priorité absolue sur le RAG pour le statut des inscriptions.

### 3. Logique de Fallback
Le fallback est géré au niveau du schéma structuré de sortie (`GuideResponse`). Si l'utilisateur pose une question hors sujet (ex: "Apprends-moi le Python"), l'agent est instruit de répondre poliment, de mettre `category="out_of_scope"`, et de forcer `information_available=false`. C'est une excellente pratique qui évite à l'agent de sortir de son rôle de guide d'admission.

## Task 7: Admin Agent & FastMCPs (`services/admin/`, `sheet-gmcp/`, `email-mcp/`)

### 1. Refactorisation en Agent ReAct
L'Agent Admin a été initialement conçu comme une preuve de concept avec un déclenchement strict par mots-clés (`if "rapport" in message`). Lors de l'audit, il a été transformé en un véritable **Agent ReAct** (Raisonnement + Action) via `langgraph.prebuilt.create_react_agent`.
- L'agent dispose d'outils explicites : `get_visitor_requests` (Postgres) et `generate_report_via_mcp` (appel MCP).
- C'est le LLM qui décide de manière autonome quand utiliser ces outils en fonction de la requête de l'administrateur.

### 2. Sécurité et Guardrails
Avant même d'invoquer le LLM, le message passe par un nœud de validation `check_guardrails`. Ce nœud inspecte le rôle de l'utilisateur (ex: `formateur`). Si un formateur tente d'accéder à des données sensibles (finance, salaire), la requête est bloquée instantanément, protégeant ainsi les données sans consommer de tokens LLM.

### 3. Serveurs FastMCP
L'architecture découplée brille grâce à l'utilisation de **FastMCP** (qui expose les outils en SSE - Server-Sent Events) :
- `email-mcp` : Fournit l'outil `send_rescheduling_email`. (Mocké pour le moment avec un délai artificiel et des logs).
- `sheet-gmcp` : Fournit l'outil `generate_admin_report`. Ce serveur se connecte réellement à l'API Google Sheets (via `gspread` et les variables d'environnement), crée un onglet et y injecte les données JSON reçues de l'Agent Admin.

## Task 8: Final Consolidation (configs, docs/main.md)

### 1. Variables d'environnement
Le fichier `.env.example` a été nettoyé :
- Suppression des résidus de configuration de `Grok` (qui a été retiré du projet).
- Mise à jour de `DATABASE_URL` pour pointer correctement vers l'URL PostgreSQL (`postgresql+psycopg://...`) au lieu du fallback SQLite initial.

### 2. Conclusion de l'Audit
Le projet **YouCode AI Agent** présente une architecture moderne, modulaire et extrêmement robuste.
- La communication inter-services via RabbitMQ RPC assure la résilience.
- L'utilisation de LangGraph permet de créer des agents aux comportements très différents (State Machine déterministe pour `newsletter`, ReAct autonome pour `guide` et `admin`).
- L'adoption du Model Context Protocol (MCP) pour la connexion aux APIs externes (Google Sheets, Email) offre une séparation propre des responsabilités et une extensibilité optimale.
