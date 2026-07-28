#!/bin/bash
set -e

echo "================================================="
echo "🚀 Bootstrapping Local EKS Simulation (Minikube)"
echo "================================================="

# 1. Start Minikube if not running
if ! minikube status >/dev/null 2>&1; then
    echo "▶️ Starting Minikube..."
    minikube start --cpus=4 --memory=8192
else
    echo "✅ Minikube is already running."
fi

# 2. Enable Ingress addon
echo "▶️ Enabling NGINX Ingress..."
minikube addons enable ingress

# 3. Install ArgoCD
echo "▶️ Installing ArgoCD..."
kubectl create namespace argocd || true
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Wait for ArgoCD server
echo "⏳ Waiting for ArgoCD server to be ready..."
kubectl wait --for=condition=Available deployment/argocd-server -n argocd --timeout=300s

# 4. Apply the Helm Chart locally via ArgoCD (or directly)
# Since we don't have the Git repository set up yet, we can apply Helm directly for testing, 
# or set up ArgoCD to point to the local path.
echo "▶️ Deploying YouCode AI Helm Chart..."
helm upgrade --install youcode-ai ./helm/youcode-ai

echo "================================================="
echo "🎉 Setup Complete!"
echo "ArgoCD UI: kubectl port-forward svc/argocd-server -n argocd 8080:443"
echo "YouCode API: http://$(minikube ip) (Requires hosts file mapping for api.youcode.local)"
echo "================================================="
