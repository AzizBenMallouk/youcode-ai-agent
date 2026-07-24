# Plan de Démonstration (Soutenance YouCode AI Platform)

**Durée totale estimée :** 3 à 5 minutes.
**Pré-requis technique :**
- Le serveur FastAPI doit tourner en local (`docker compose up -d`).
- Le webhook WhatsApp doit être branché (via le conteneur `whatsapp-bot` ou Ngrok si on teste en live).
- Un téléphone avec WhatsApp ouvert (pour montrer l'écran) ou WhatsApp Web projeté.
- Un onglet ouvert sur le fichier Google Sheets "YouCode Admin Dashboard" utilisé par MCP.

---

## Scénario 1 : Le RAG Institutionnel (1 minute)
**But :** Prouver que l'agent répond uniquement aux questions dont la réponse se trouve dans les documents YouCode, sans hallucinations.

1. **Jury (ou vous) tapez sur WhatsApp :** *"Bonjour, c'est quoi YouCode ?"*
2. **Attendez la réponse.** L'agent doit répondre par une introduction générale issue du RAG.
3. **Tapez :** *"Je n'ai pas de baccalauréat, est-ce que je peux postuler ?"*
4. **Attendez la réponse.** L'agent (Guide) doit affirmer que le Bac n'est pas obligatoire, confirmant qu'il extrait bien l'information du RAG.
5. *(Optionnel : Piège)* **Tapez :** *"Combien coûte une chambre d'hôtel près du campus de Youssoufia ?"*
   - **Réponse attendue :** L'agent indique gentiment qu'il ne dispose pas de cette information (Démonstration de l'anti-hallucination).

---

## Scénario 2 : Le Report de Test (Support) (2 minutes)
**But :** Prouver l'orchestration LangGraph, l'interruption d'état (State) et la persistance via MCP vers Google Sheets.

1. **Tapez :** *"J'ai un problème, je veux reporter mon test d'admission."*
2. **Observation :** L'agent Support prend le relais. Comme il lui manque des informations pour son extraction Pydantic, il va demander des précisions.
3. **L'agent répond :** *"Pouvez-vous m'indiquer votre e-mail et le campus concerné ?"*
4. **Tapez :** *"C'est Safi, mon email est test@example.com."*
5. **Observation :** L'agent synthétise la demande et demande un consentement explicite.
6. **Tapez :** *"Oui, j'accepte."*
7. **Action manuelle :** Basculez l'écran sur l'onglet **Google Sheets**.
8. **Observation :** Montrez au jury que la nouvelle demande vient d'apparaître instantanément dans le tableur (grâce à SQLAlchemy Events + MCP).
9. **L'agent répond (WhatsApp) :** *"Votre demande a été enregistrée. Voici les prochaines sessions disponibles..."*

---

## Scénario 3 : Inscription Newsletter (1 minute)
**But :** Montrer la flexibilité du système et la collecte d'informations optionnelles.

1. **Tapez :** *"Je veux être alerté des prochaines ouvertures d'inscriptions."*
2. **L'agent répond :** *"Quel est votre email et êtes-vous plutôt intéressé par la formation classique ou les bootcamps ?"*
3. **Tapez :** *"Les deux. test-news@example.com."*
4. **L'agent demande :** *"Confirmez-vous l'abonnement ?"*
5. **Tapez :** *"Oui."*
6. **Action manuelle :** Retournez sur le fichier Google Sheets, onglet "Newsletter".
7. **Observation :** La nouvelle ligne est ajoutée avec les tags correspondants.

---

## PLAN B (Scénario de Secours)
**Important :** En soutenance, "l'effet démo" est fréquent (panne de réseau, erreur d'API, blocage de compte WhatsApp). 

Si quoi que ce soit bloque en direct :
1. Ne paniquez pas et n'essayez pas de débugger le code en live.
2. Dites simplement : *"Les aléas du direct font que le réseau/l'API est inaccessible. J'ai cependant enregistré une vidéo de ce même processus hier."*
3. Ouvrez le dossier `docs/presentation/screenshots/` ou lancez votre vidéo de secours pré-enregistrée montrant exactement le déroulé ci-dessus.
4. L'important est de montrer la valeur métier au jury, pas que l'API externe fonctionne à l'instant T.
