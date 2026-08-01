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

# Check for Google Credentials in secrets folder
if [ -f "secrets/google_credentials.json" ]; then
    echo "▶️ Injecting Google Credentials into Kubernetes secret 'google-credentials'..."
    kubectl create secret generic google-credentials --from-file=credentials.json=secrets/google_credentials.json -o yaml --dry-run=client | kubectl apply -f -
else
    echo "⚠️ Warning: secrets/google_credentials.json not found. Google Sheets MCP may not work."
fi

# Create ConfigMap for LiteLLM
if [ -f "config/litellm_config.yaml" ]; then
    echo "▶️ Injecting LiteLLM Config into Kubernetes ConfigMap 'litellm-config'..."
    kubectl create configmap litellm-config --from-file=config.yaml=config/litellm_config.yaml -o yaml --dry-run=client | kubectl apply -f -
else
    echo "⚠️ Warning: config/litellm_config.yaml not found. LiteLLM may not start properly."
fi

echo "✅ Secrets successfully synchronized!"
echo ""
echo "💡 Note: Existing pods do not automatically reload secrets."
echo "If you want to apply these new secrets immediately to your microservices, run:"
echo "kubectl rollout restart deployment"
echo "================================================="
