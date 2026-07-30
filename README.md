# YouCode AI Agent - Architecture Microservices & GitOps

Ce projet déploie une flotte d'agents d'Intelligence Artificielle intégrés à WhatsApp (via Evolution API) pour automatiser le support, les inscriptions, et les workflows de YouCode.

Le système utilise une architecture de **Microservices** et est conçu pour être déployé sur **Kubernetes (EKS)** en respectant la philosophie **GitOps**.

---

## 🏗 Architecture & GitOps (Le Workflow CI/CD)

Notre système utilise un paradigme **GitOps** stict, séparant le code source de l'état de l'infrastructure :

1. **Dépôt Application (`youcode-ai-agent`)** : Contient le code métier Python (FastAPI, LangGraph).
2. **Dépôt Infrastructure (`youcode-ai-gitops`)** : Contient l'état désiré du cluster (Manifestes Helm Kubernetes).

### Comment ça marche ?
1. Un développeur pousse du code sur la branche `main` de ce dépôt.
2. **GitHub Actions (CI)** se déclenche : il construit les images Docker de tous les microservices et les pousse vers le registre cloud (Amazon ECR).
3. Le workflow CI **modifie automatiquement** le fichier `values.yaml` dans le second dépôt (`youcode-ai-gitops`) avec le nouveau tag d'image, puis fait un commit automatique.
4. **ArgoCD (CD)**, installé dans le cluster Kubernetes, détecte le changement sur le dépôt GitOps, et synchronise instantanément le cluster (déploiements sans coupure).

---

## 🚀 Lancer le projet en Local (Simulation Minikube)

Vous n'avez pas besoin d'un compte AWS pour tester le flux complet. Nous avons préparé un environnement de simulation local ultra-réaliste.

### Prérequis
- `minikube` installé.
- `kubectl` et `helm` installés.

### Démarrage Automatique
Exécutez simplement notre script d'amorçage :
```bash
chmod +x setup-local-eks.sh
./setup-local-eks.sh
```

Ce script va :
1. Démarrer un cluster Minikube local.
2. Activer l'Ingress NGINX.
3. Installer ArgoCD pour le déploiement continu.
4. Appliquer la Stack `Helm` (Bases de données StatefulSets, APIs, et Agents).

*(Alternative : Vous pouvez toujours utiliser `docker compose up -d --build` si vous voulez juste tester le code sans Kubernetes).*

---

## 📱 Connecter WhatsApp (Interface QR)

L'application utilise **Evolution API** pour brancher l'IA directement sur WhatsApp. Nous avons ajouté une interface web minimale pour scanner le QR Code très facilement.

### Étape 1 : Créer l'instance dans Evolution API
Si c'est votre première exécution, demandez à l'API de créer l'instance "youcode-ai" :
```bash
curl -X POST http://localhost:8080/instance/create \
  -H "Content-Type: application/json" \
  -H "apikey: B6D711FCDE4D4FD5936544120E713976" \
  -d '{
    "instanceName": "youcode-ai",
    "qrcode": true,
    "integration": "WHATSAPP-BAILEYS"
}'
```
*(Si vous êtes sur Minikube, remplacez `localhost:8080` par `api.youcode.local/evolution`).*

### Étape 2 : Scanner le QR Code via l'Interface Web
Ouvrez simplement votre navigateur à l'adresse suivante :
👉 **http://localhost:8000/qr**
*(Sur Minikube : `http://api.youcode.local/qr`)*

Une belle page minimale s'ouvrira, affichant le QR Code WhatsApp en direct.
1. Ouvrez WhatsApp sur le téléphone "Bot".
2. Allez dans **Appareils connectés** > **Connecter un appareil**.
3. Scannez le QR code affiché à l'écran. 

Le tour est joué, le Bot est en ligne !

### Étape 3 : Tester l'Agent
Demandez à quelqu'un d'envoyer un message au numéro connecté (ex: *"J'ai besoin de reporter mon test de demain"*). La Gateway intercepte le webhook, l'envoie à l'Orchestrateur LangGraph, qui délègue la tâche au bon agent (Support). L'agent peut même utiliser Google Sheets de manière autonome.

---

### 💡 Astuce de Debugging
Si vous voulez voir en direct comment l'IA réfléchit, consultez les logs de l'orchestrateur :
```bash
kubectl logs -f deployment/orchestrator
# Ou si vous êtes sous Docker : docker compose logs -f orchestrator
```
