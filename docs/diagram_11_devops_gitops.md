# 5. Diagramme DevOps & GitOps (CI/CD)

Ce diagramme illustre le flux de travail complet de l'Intégration Continue (CI) et du Déploiement Continu (CD) basé sur **GitOps**. Il montre comment le code source passe du dépôt GitHub au cluster Kubernetes via GitHub Actions, Amazon ECR et ArgoCD.

> [!TIP]
> **Comment l'utiliser dans Eraser.io :**
> Importez ce code Mermaid directement dans Eraser ou donnez-le à l'IA d'Eraser pour qu'elle le transforme en vue architecturale détaillée.

```mermaid
graph TD
    %% Développeur et Dépôts
    Dev(("Développeur"))
    AppRepo["GitHub: Dépôt Application<br/>(youcode-ai-agent)"]
    GitOpsRepo["GitHub: Dépôt GitOps<br/>(youcode-ai-gitops)"]
    
    %% CI: GitHub Actions
    subgraph "CI Pipeline (GitHub Actions)"
        BuildTest["Build & Test"]
        DockerBuild["Docker Build"]
        PushECR["Push Image to Registry"]
        UpdateTag["Update Helm values.yaml<br/>(Commit & Push)"]
    end
    
    %% Registre Docker
    Registry[("Amazon ECR / Docker Hub<br/>(Image Registry)")]
    
    %% Cluster Kubernetes (EKS ou Minikube)
    subgraph "Cluster Kubernetes (EKS / Minikube)"
        ArgoCD["ArgoCD<br/>(GitOps Controller)"]
        
        subgraph "Helm Deployment: youcode-ai"
            Ingress["NGINX Ingress"]
            Microservices["Deployments<br/>(API, Orchestrator, Agents)"]
            StatefulSets[("StatefulSets<br/>(Postgres, Redis, Qdrant)")]
        end
    end
    
    %% Flux CI
    Dev -->|"git push (code source)"| AppRepo
    AppRepo -->|"Declenche webhook"| BuildTest
    BuildTest --> DockerBuild
    DockerBuild --> PushECR
    PushECR -->|"Upload image"| Registry
    PushECR -->|"Ensuite"| UpdateTag
    UpdateTag -->|"git commit (nouveau tag)"| GitOpsRepo
    
    %% Flux CD (GitOps)
    ArgoCD -->|"Observe / Sync"| GitOpsRepo
    ArgoCD -->|"Pull nouvelle image"| Registry
    ArgoCD -->|"Applique changements<br/>(Helm Upgrade)"| Ingress
    ArgoCD -->|"Applique changements<br/>(Helm Upgrade)"| Microservices
    ArgoCD -->|"Applique changements<br/>(Helm Upgrade)"| StatefulSets
    
    %% Trafic utilisateur final
    Users(("Utilisateurs / WhatsApp"))
    Users -->|"Requêtes HTTP"| Ingress
    Ingress --> Microservices
    Microservices <--> StatefulSets

    %% Styles
    classDef actor fill:#f39c12,stroke:#e67e22,color:#ffffff,stroke-width:2px
    classDef repo fill:#2c3e50,stroke:#34495e,color:#ffffff,stroke-width:2px
    classDef ci fill:#8e44ad,stroke:#9b59b6,color:#ffffff,stroke-width:2px
    classDef registry fill:#27ae60,stroke:#2ecc71,color:#ffffff,stroke-width:2px
    classDef k8s fill:#2980b9,stroke:#3498db,color:#ffffff,stroke-width:2px
    classDef k8scomp fill:#ecf0f1,stroke:#bdc3c7,color:#2c3e50,stroke-width:2px

    class Dev,Users actor
    class AppRepo,GitOpsRepo repo
    class BuildTest,DockerBuild,PushECR,UpdateTag ci
    class Registry registry
    class ArgoCD,Ingress,Microservices k8s
    class StatefulSets k8scomp
```
