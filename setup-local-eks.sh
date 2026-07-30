#!/bin/bash
set -e

echo "================================================="
echo "🚀 Bootstrapping Local EKS Simulation (Minikube)"
echo "================================================="

# 1. Start Minikube if not running
if ! minikube status >/dev/null 2>&1; then
    echo "▶️ Starting Minikube..."
    minikube start
else
    echo "✅ Minikube is already running."
fi

# 2. Enable Ingress addon
echo "▶️ Enabling NGINX Ingress..."
minikube addons enable ingress

# 3. Install ArgoCD
echo "▶️ Installing ArgoCD..."
kubectl create namespace argocd || true
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml --server-side --force-conflicts

# Wait for ArgoCD server
echo "⏳ Waiting for ArgoCD server to be ready..."
kubectl wait --for=condition=Available deployment/argocd-server -n argocd --timeout=300s

# 4. Build local images inside Minikube
echo "▶️ Building local Docker images in Minikube..."
eval $(minikube -p minikube docker-env)

# Evolution API
docker pull evoapicloud/evolution-api:latest
docker tag evoapicloud/evolution-api:latest youcode/evolution-api:local

# Microservices
docker build -t youcode/gateway:local -f services/gateway/Dockerfile .
docker build -t youcode/orchestrator:local -f services/orchestrator/Dockerfile .
docker build -t youcode/support:local -f services/support/Dockerfile .
docker build -t youcode/guide:local -f services/guide/Dockerfile .
docker build -t youcode/newsletter:local -f services/newsletter/Dockerfile .
docker build -t youcode/sheet-gmcp:local -f services/sheet-gmcp/Dockerfile .

# 5. Configure ArgoCD to track the GitOps repository
echo "▶️ Deploying YouCode AI via ArgoCD (GitOps)..."
cat <<EOF | kubectl apply -f -
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: youcode-ai
  namespace: argocd
spec:
  project: default
  source:
    repoURL: 'https://github.com/AzizBenMallouk/youcode-ai-gitops.git'
    path: helm/youcode-ai
    targetRevision: HEAD
    helm:
      parameters:
        - name: "evolution.image.tag"
          value: "local"
        - name: "microservices.gateway.image.tag"
          value: "local"
        - name: "microservices.orchestrator.image.tag"
          value: "local"
        - name: "microservices.support.image.tag"
          value: "local"
        - name: "microservices.newsletter.image.tag"
          value: "local"
        - name: "microservices.guide.image.tag"
          value: "local"
        - name: "microservices.sheet_gmcp.image.tag"
          value: "local"
  destination:
    server: 'https://kubernetes.default.svc'
    namespace: default
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
EOF

echo "================================================="
echo "🎉 Setup Complete!"
echo "ArgoCD UI: kubectl port-forward svc/argocd-server -n argocd 8080:443"
echo "YouCode API: http://$(minikube ip) (Requires hosts file mapping for api.youcode.local)"
echo "================================================="
