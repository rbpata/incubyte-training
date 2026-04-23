# Kubernetes Deployment Guide

## Prerequisites
- Kubernetes cluster (v1.28+)
- kubectl configured
- Docker images built and pushed to registry
- cert-manager (for TLS)
- nginx-ingress-controller

## Quick Start

### 1. Deploy Infrastructure
```bash
# Apply all manifests in order
kubectl apply -f k8s/00-namespace.yaml
kubectl apply -f k8s/01-configmap.yaml
kubectl apply -f k8s/02-secrets.yaml
kubectl apply -f k8s/03-postgres.yaml

# Wait for DB to be ready
kubectl wait --for=condition=ready pod -l app=postgres -n taskscheduler --timeout=120s

# Run migrations
kubectl apply -f k8s/12-db-migration.yaml
kubectl wait --for=condition=complete job/db-migration -n taskscheduler --timeout=60s

# Deploy services
kubectl apply -f k8s/04-auth-service.yaml
kubectl apply -f k8s/05-task-service.yaml
kubectl apply -f k8s/06-api-gateway.yaml
kubectl apply -f k8s/07-frontend.yaml

# Deploy monitoring and policies
kubectl apply -f k8s/08-ingress.yaml
kubectl apply -f k8s/09-resource-limits.yaml
kubectl apply -f k8s/10-network-policies.yaml
kubectl apply -f k8s/11-hpa.yaml
```

Or deploy all at once:
```bash
kubectl apply -f k8s/
```

### 2. Verify Deployment
```bash
# Check all resources
kubectl get all -n taskscheduler

# Check pod status
kubectl get pods -n taskscheduler -w

# Check service endpoints
kubectl get svc -n taskscheduler

# Check HPA status
kubectl get hpa -n taskscheduler
```

### 3. Access Application
```bash
# Port forward to frontend (local dev)
kubectl port-forward -n taskscheduler svc/frontend 8080:80

# Port forward to API gateway
kubectl port-forward -n taskscheduler svc/api-gateway 8000:8000

# Access via ingress (after configuring DNS)
# https://taskscheduler.example.com
```

## Configuration

### Update Secrets
```bash
# Edit secrets (base64 encoded in K8s)
kubectl edit secret taskscheduler-secrets -n taskscheduler

# Or create from .env file
kubectl create secret generic taskscheduler-secrets \
  --from-env-file=.env \
  -n taskscheduler \
  -o yaml --dry-run=client | kubectl apply -f -
```

### Update ConfigMap
```bash
kubectl edit configmap taskscheduler-config -n taskscheduler
```

### Environment-specific deployments
Create overlays with Kustomize:
```
k8s/
  base/
    kustomization.yaml
    ...manifests...
  overlays/
    prod/
      kustomization.yaml
    staging/
      kustomization.yaml
```

Deploy specific overlay:
```bash
kubectl apply -k k8s/overlays/prod
```

## Monitoring

### Prometheus
```bash
kubectl port-forward -n taskscheduler svc/prometheus 9090:9090
# Visit http://localhost:9090
```

### Grafana
```bash
kubectl port-forward -n taskscheduler svc/grafana 3000:3000
# Visit http://localhost:3000
# User: admin, Password: (from secret)
```

## Scaling

HPA configured for CPU/memory utilization. Manual scaling:
```bash
kubectl scale deployment auth-service --replicas=3 -n taskscheduler
```

Check HPA status:
```bash
kubectl describe hpa auth-service-hpa -n taskscheduler
```

## Logs

View service logs:
```bash
kubectl logs -f deployment/auth-service -n taskscheduler
kubectl logs -f deployment/task-service -n taskscheduler
kubectl logs -f deployment/api-gateway -n taskscheduler
kubectl logs -f deployment/frontend -n taskscheduler
```

## Database Operations

### Connect to PostgreSQL
```bash
kubectl exec -it postgres-0 -n taskscheduler -- psql -U postgres -d taskscheduler
```

### Run Alembic migrations manually
```bash
kubectl run -it --rm db-migration-manual \
  --image=taskscheduler/auth-service:latest \
  --restart=Never \
  -n taskscheduler \
  -- /bin/sh -c 'uv run alembic upgrade head'
```

## Troubleshooting

### Pod not starting
```bash
# Check pod status
kubectl describe pod <pod-name> -n taskscheduler

# Check logs
kubectl logs <pod-name> -n taskscheduler
kubectl logs <pod-name> -n taskscheduler --previous
```

### Readiness probe failures
```bash
# Check if service is responding
kubectl exec -it <pod-name> -n taskscheduler -- curl -v http://localhost:8000/health
```

### Database connection errors
```bash
# Check if postgres is running
kubectl get pod postgres-0 -n taskscheduler
kubectl logs postgres-0 -n taskscheduler

# Test connection from a service pod
kubectl exec -it <service-pod> -n taskscheduler -- \
  python -c "import psycopg2; psycopg2.connect('postgresql://...')"
```

### Storage issues
```bash
# Check PVC status
kubectl get pvc -n taskscheduler
kubectl describe pvc postgres-pvc -n taskscheduler
```

## Rollback

Rollback deployment to previous version:
```bash
kubectl rollout history deployment/auth-service -n taskscheduler
kubectl rollout undo deployment/auth-service -n taskscheduler --to-revision=1
```

Monitor rollout:
```bash
kubectl rollout status deployment/auth-service -n taskscheduler -w
```
