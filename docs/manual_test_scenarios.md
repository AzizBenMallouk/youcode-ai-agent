# 🧪 Scénarios de Test Complets (Validation E2E)

Voici la liste complète des scénarios pour tester chaque fonctionnalité et règle métier de l'architecture microservices. 

> [!IMPORTANT]
> **Prérequis :** Assurez-vous que l'ensemble du système tourne sur votre machine via `docker compose up -d` ou `docker compose up --build`. L'API Gateway écoute sur le port `8000`.

---

## Scénario 1 : Le Guardrail et le Hors-Sujet (Orchestrateur)
**Objectif :** Vérifier que l'Orchestrateur bloque les questions non pertinentes sans réveiller les agents distants.

- **Requête (cURL) :**
  ```bash
  curl -X POST http://localhost:8000/api/v1/whatsapp/webhook \
    -H "Content-Type: application/json" \
    -d '{"data": {"key": {"remoteJid": "212600000000"}, "message": {"conversation": "Quelle est la recette de la tarte aux pommes ?"}}}'
  ```
- **Résultat Attendu :** La réponse JSON contient `active_agent: orchestrator` et un message de refus poli (ex: *"Je suis l'assistant YouCode, je ne peux pas répondre à cette question"*). Les logs de `guide`, `support` et `newsletter` doivent être vides.

---

## Scénario 2 : L'Agent Guide (RAG / Informations)
**Objectif :** Vérifier que le routage vers l'Agent Guide fonctionne et qu'il interroge correctement la base Qdrant.

- **Requête (cURL) :**
  ```bash
  curl -X POST http://localhost:8000/api/v1/whatsapp/webhook \
    -H "Content-Type: application/json" \
    -d '{"data": {"key": {"remoteJid": "212600000001"}, "message": {"conversation": "Comment se déroule la pédagogie active à YouCode ?"}}}'
  ```
- **Résultat Attendu :** L'Orchestrateur route vers le Guide. La réponse (`active_agent: guide`) fournit des informations sur la pédagogie active.
- **Vérification DB :** Vous devriez voir une entrée `guide_212600000001` dans la table `checkpoints`.

---

## Scénario 3 : L'Agent Support (Flux Conversationnel Complexe)
**Objectif :** Vérifier que le Support garde la mémoire de la conversation, collecte des informations, et gère l'état (State) de l'utilisateur.

- **Étape 3.1 : Initialisation**
  ```bash
  curl -X POST http://localhost:8000/api/v1/whatsapp/webhook \
    -H "Content-Type: application/json" \
    -d '{"data": {"key": {"remoteJid": "212600000002"}, "message": {"conversation": "Je veux reporter mon test d admission."}}}'
  ```
  *Résultat Attendu :* Le Support (`active_agent: support`) vous demande des informations manquantes (ex: *"Quel est votre nom et votre numéro CIN ?"*).

- **Étape 3.2 : Fourniture des données**
  ```bash
  curl -X POST http://localhost:8000/api/v1/whatsapp/webhook \
    -H "Content-Type: application/json" \
    -d '{"data": {"key": {"remoteJid": "212600000002"}, "message": {"conversation": "Mon nom est Ahmed, mon CIN est AB123456"}}}'
  ```
  *Résultat Attendu :* L'agent se souvient que la conversation concerne le "report de test". Il valide l'extraction et vous demande de confirmer (Consentement).

- **Étape 3.3 : Confirmation**
  ```bash
  curl -X POST http://localhost:8000/api/v1/whatsapp/webhook \
    -H "Content-Type: application/json" \
    -d '{"data": {"key": {"remoteJid": "212600000002"}, "message": {"conversation": "Oui je confirme."}}}'
  ```
  *Résultat Attendu :* L'agent traite la demande. 

---

## Scénario 4 : L'Agent Newsletter (Flux de Souscription)
**Objectif :** Vérifier le flux conversationnel indépendant de la Newsletter.

- **Requête (cURL) :**
  ```bash
  curl -X POST http://localhost:8000/api/v1/whatsapp/webhook \
    -H "Content-Type: application/json" \
    -d '{"data": {"key": {"remoteJid": "212600000003"}, "message": {"conversation": "Je veux minscrire a la newsletter."}}}'
  ```
- **Résultat Attendu :** Le Supervisor route vers `newsletter`. L'agent vous demande votre adresse e-mail.

---

## Scénario 5 : Vérification Stricte de l'Isolation des Données (Privacy)
**Objectif :** S'assurer que le Guide ou l'Orchestrateur n'a **pas** accès au CIN donné au Support au Scénario 3.

- **Requête (cURL) utilisant le même numéro de téléphone que le Scénario 3 :**
  ```bash
  curl -X POST http://localhost:8000/api/v1/whatsapp/webhook \
    -H "Content-Type: application/json" \
    -d '{"data": {"key": {"remoteJid": "212600000002"}, "message": {"conversation": "Peux-tu me rappeler mon numéro de CIN ?"}}}'
  ```
- **Résultat Attendu :** 
  L'Orchestrateur va router cela soit au Guardrail (si détecté comme confidentiel), soit au Guide/Clarification. 
  Puisque le State est isolé (`guide_212600000002` ou `orch_212600000002` vs `support_212600000002`), **l'agent répondra qu'il ne connait pas votre CIN**.
  C'est la preuve absolue que notre isolation par agent fonctionne !

---

## Scénario 6 : Résilience et Tolérance aux Pannes
**Objectif :** Vérifier la résilience de notre Wrapper (Tenacity) en cas d'indisponibilité d'un service.

- **Étape 1 :** Tuer le conteneur du Guide
  ```bash
  docker compose stop guide
  ```
- **Étape 2 :** Poser une question sur YouCode (Routage vers Guide attendu)
  ```bash
  curl -X POST http://localhost:8000/api/v1/whatsapp/webhook \
    -H "Content-Type: application/json" \
    -d '{"data": {"key": {"remoteJid": "212600000004"}, "message": {"conversation": "C est quoi YouCode ?"}}}'
  ```
- **Résultat Attendu :**
  - Vous verrez dans les logs de `orchestrator` que le client A2A tente de se connecter, échoue, attend (2s, puis 4s, etc.), puis abandonne.
  - La réponse finale renvoyée à cURL sera un message gracieux : *"Le service guide est temporairement indisponible."* plutôt qu'une erreur 500 ou un crash de l'API.

---

## Scénario 7 : Base de Données Persistante
**Objectif :** S'assurer que si un agent redémarre, l'utilisateur ne perd pas sa conversation.

- **Étape 1 :** Envoyer *"Je veux contacter le support"* depuis un numéro.
- **Étape 2 :** Tuer puis relancer le support (`docker compose restart support`).
- **Étape 3 :** Envoyer la suite *"C'est pour mon test"*.
- **Résultat Attendu :** Le Support se souvient du premier message car il l'a lu depuis `AsyncPostgresSaver` dans la DB.
