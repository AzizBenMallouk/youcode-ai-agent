#!/bin/bash
set -e

echo "================================================="
echo "🔒 Syncing secrets from local .env to Minikube"
echo "================================================="

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found in the current directory."
    echo "Please ensure you are running this from the project root."
    exit 1
fi

# Check if Minikube/Kubernetes is accessible
if ! kubectl cluster-info >/dev/null 2>&1; then
    echo "❌ Error: Cannot connect to the Kubernetes cluster."
    echo "Is Minikube running?"
    exit 1
fi

# Create or update the secret in Kubernetes
# Using --dry-run=client | apply -f - allows us to update the secret if it already exists
echo "▶️ Injecting secrets from .env into Kubernetes secret 'youcode-secrets'..."
kubectl create secret generic youcode-secrets --from-env-file=.env -o yaml --dry-run=client | kubectl apply -f -

echo "✅ Secrets successfully synchronized!"
echo ""
echo "💡 Note: Existing pods do not automatically reload secrets."
echo "If you want to apply these new secrets immediately to your microservices, run:"
echo "kubectl rollout restart deployment"
echo "================================================="
