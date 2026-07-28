# YouCode AI Agent - Guide de Démarrage WhatsApp

L'application utilise **Evolution API** pour faire le pont entre WhatsApp et nos agents d'intelligence artificielle. Evolution API se charge de recevoir les messages WhatsApp, de les envoyer à notre `Gateway`, et de renvoyer la réponse de l'IA à l'utilisateur.

Voici les étapes complètes pour connecter votre propre téléphone et tester l'application en conditions réelles :

## Étape 1 : Vérifier que les services tournent
Si ce n'est pas déjà fait, lancez toute l'infrastructure (Postgres, Qdrant, Redis, Evolution API, Gateway, Orchestrateur, et les Agents) :
```bash
docker compose up -d
```
Vous pouvez vérifier que Evolution API tourne bien sur le port `8090` :
```bash
docker compose ps
```

## Étape 2 : Créer une Instance WhatsApp sur Evolution API
Pour connecter un numéro, nous devons d'abord créer une "Instance" dans Evolution API. 

Exécutez cette commande dans votre terminal. Elle va créer l'instance `test_instance` et générer le QR Code :
```bash
curl -X POST http://localhost:8090/instance/create \
  -H "Content-Type: application/json" \
  -H "apikey: super_secret_key" \
  -d '{
    "instanceName": "test_instance",
    "qrcode": true,
    "integration": "WHATSAPP-BAILEYS"
}'
```

*(Note : Evolution API est configuré via `compose.yaml` pour brancher automatiquement les webhooks globaux sur notre Gateway `http://gateway:8000/api/v1/whatsapp/webhook`, vous n'avez donc pas besoin de configurer les webhooks manuellement !)*

## Étape 3 : Scanner le QR Code
La requête ci-dessus vous retournera une réponse JSON contenant une clé `"qrcode"` avec une chaîne en `base64`. 

Pour l'afficher et la scanner :
1. Copiez la valeur en `base64` (sans les guillemets).
2. Allez sur un convertisseur en ligne comme [Base64 to Image](https://codebeautify.org/base64-to-image-converter).
3. Collez la chaîne, cela affichera le QR code.
4. Ouvrez WhatsApp sur le téléphone que vous voulez utiliser comme "Bot".
5. Allez dans **Appareils connectés** > **Connecter un appareil** et scannez le QR code.

*Alternative (Plus simple)* : Vous pouvez utiliser Postman ou Insomnia pour lancer la requête `POST` précédente, beaucoup d'outils convertissent automatiquement le `base64` en image !

## Étape 4 : Interagir !
1. Demandez à un ami (ou utilisez un autre numéro de téléphone) d'envoyer un message au numéro que vous venez de connecter (le Bot).
2. Envoyez par exemple : `"Salut, c'est quoi YouCode ?"`
3. L'événement passera par Evolution API -> Gateway -> Orchestrateur -> Agent Guide. L'agent formulera une réponse qui redescendra automatiquement vers WhatsApp.

### 💡 Astuce de Debugging
Si vous voulez voir en direct comment les requêtes circulent entre les agents, ouvrez un terminal et affichez les logs en temps réel :
```bash
docker compose logs -f gateway orchestrator support guide
```

Et voilà ! Votre bot WhatsApp intelligent est officiellement en ligne 🚀.
