# Guide d'Installation et d'Utilisation sur Minikube 🚀

Ce document explique comment lancer le projet YouCode AI Agent localement via **Minikube** (qui simule un cluster Kubernetes), et détaille toutes les commandes pratiques pour tester, relancer et déboguer l'application.

---

## 1. 🚀 Démarrer l'Application

Le script `setup-local-eks.sh` automatise entièrement le déploiement local (démarrage de Minikube, build des images Docker, et déploiement Kubernetes).

1. Ouvrez votre terminal à la racine du projet.
2. Lancez le script de démarrage :
   ```bash
   ./setup-local-eks.sh
   ```

*Ce script va prendre soin de démarrer Minikube avec suffisamment de mémoire (4Go), construire toutes les images, et appliquer les manifests.*

---

## 2. 📱 Scanner le QR Code WhatsApp (via Port-Forward)

Pour connecter l'agent à votre compte WhatsApp, vous devez accéder à la page web générant le QR Code depuis le service `whatsapp-gateway`.

1. **Redirigez le port** de ce service vers votre machine locale :
   ```bash
   kubectl port-forward svc/whatsapp-gateway 8000:8000
   ```
2. **Ouvrez votre navigateur** à cette adresse :
   **[http://localhost:8000/qr](http://localhost:8000/qr)**
3. **Scannez le QR Code** depuis votre téléphone (Appareils connectés > Connecter un appareil).

> [!TIP]
> Tant que la commande `port-forward` tourne dans votre terminal, l'accès local fonctionne. Appuyez sur `Ctrl+C` pour l'arrêter quand vous avez terminé.

---

## 3. 🧪 Tester l'App via cURL (Sans WhatsApp)

Si vous voulez envoyer un message à l'IA et voir sa réponse directement dans votre terminal sans utiliser WhatsApp, vous pouvez attaquer le service `orchestrator` directement.

1. **Redirigez le port** de l'orchestrateur (dans un nouveau terminal) :
   ```bash
   kubectl port-forward svc/orchestrator 8006:8006
   ```

2. **Envoyez une requête cURL** pour simuler une discussion :
   ```bash
   curl -X POST http://localhost:8006/chat \
     -H "Content-Type: application/json" \
     -d '{
       "session_id": "test-session-123",
       "message": "Bonjour, quand commencent les inscriptions ?",
       "user_phone": "212600000000"
     }'
   ```
   *(Modifiez le champ "message" pour tester différents agents comme le Guide ou le Support).*

---

## 4. 🔄 Commandes de Restart (En cas de modification du code)

Si vous modifiez le code Python d'un service (par exemple `guide`, `whatsapp-gateway`, ou `fake-registration-api`), vous devez reconstruire son image Docker dans Minikube et relancer le pod.

**Étape 1 : Mettre à jour les variables Kubernetes**
Si vous avez ajouté de nouvelles clés d'API (comme `DISCORD_BOT_TOKEN`), appliquez-les d'abord aux secrets de Minikube :
```bash
./apply-secrets.sh
```

**Étape 2 : Se connecter à l'environnement Docker de Minikube**
```bash
eval $(minikube -p minikube docker-env)
```

**Étape 3 : Re-builder l'image du service modifié** (exemple pour le *guide*)
```bash
docker build -t youcode/guide:local -f services/guide/Dockerfile .
```

**Étape 4 : Redémarrer le déploiement Kubernetes** pour forcer l'utilisation de la nouvelle image :
```bash
kubectl rollout restart deployment guide
```

*(Remplacez `guide` par le nom du service que vous avez modifié, ex: `whatsapp-gateway`, `orchestrator`, `support`)*

---

## 5. 🛠️ Débogage Courant

**Voir les logs en direct d'un service (ex: l'orchestrateur) :**
```bash
kubectl logs -l app=orchestrator -f
```

**Voir tous les pods pour vérifier s'il y a des erreurs :**
```bash
kubectl get pods -A
```

**Accéder à l'interface d'ArgoCD (GitOps) :**
```bash
kubectl port-forward svc/argocd-server -n argocd 8080:443
# Ensuite, ouvrez https://localhost:8080 (Login: admin)
```
*(Mot de passe par défaut d'ArgoCD : `kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d; echo`)*
