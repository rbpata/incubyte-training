# TaskScheduler Production Deployment Guide

## Architecture Overview

```
                    Internet
                       ↓
                   [Ingress/LB]
                    ↙    ↓    ↘
            [Frontend]  [API Gateway]
                        ↙      ↘
                    [Auth]   [Task]
                        ↘    ↙
                    [PostgreSQL]
                        ↓
                  [Prometheus]
                        ↓
                    [Grafana]
```

### Components

**Frontend (nginx)**
- Serves static React SPA
- Caches versioned assets (1 year)
- Fallback to index.html for SPA routing
- 2+ replicas for HA

**API Gateway (FastAPI)**
- Routes requests to microservices
- Request/response logging
- CORS handling
- Rate limiting (if configured)
- 2+ replicas for HA

**Auth Service (FastAPI)**
- User authentication
- Token management
- 2+ replicas for HA
- Horizontal scaling on CPU/memory

**Task Service (FastAPI)**
- Task CRUD operations
- 2+ replicas for HA
- Horizontal scaling on CPU/memory

**PostgreSQL**
- Single StatefulSet (1 replica)
- Persistent volume (10GB default)
- Connection pooling
- Health checks

**Monitoring**
- Prometheus: Metrics collection (30s interval)
- Grafana: Visualization & dashboards
- Alert rules: Critical/warning alerts

## Deployment Methods

### 1. Docker Compose (Local Development)

```bash
cd backend/services

# Configure environment
cp .env.example .env
# Edit .env with actual values

# Build and start
docker-compose up -d

# Verify
docker-compose ps
docker-compose logs -f api-gateway

# Access
curl http://localhost:8000/health
open http://localhost  # Frontend
open http://localhost:3001  # Grafana (admin/admin)
```

### 2. Kubernetes (Production)

#### Prerequisites
- K8s cluster 1.28+
- kubectl configured
- Docker images pushed to registry
- Storage provisioner (for DB PVC)
- Ingress controller (nginx)

#### Deploy

```bash
cd backend/services/k8s

# 1. Namespace & configs
kubectl apply -f 00-namespace.yaml
kubectl apply -f 01-configmap.yaml
kubectl apply -f 02-secrets.yaml

# 2. Database
kubectl apply -f 03-postgres.yaml
kubectl wait --for=condition=ready pod -l app=postgres -n taskscheduler --timeout=120s

# 3. Run migrations
kubectl apply -f 12-db-migration.yaml
kubectl wait --for=condition=complete job/db-migration -n taskscheduler --timeout=60s

# 4. Services
kubectl apply -f 04-auth-service.yaml
kubectl apply -f 05-task-service.yaml
kubectl apply -f 06-api-gateway.yaml
kubectl apply -f 07-frontend.yaml

# 5. Infrastructure
kubectl apply -f 08-ingress.yaml
kubectl apply -f 09-resource-limits.yaml
kubectl apply -f 10-network-policies.yaml
kubectl apply -f 11-hpa.yaml

# Verify
kubectl get all -n taskscheduler
```

## Configuration

### Environment Variables

**Application (ConfigMap)**
```yaml
ENVIRONMENT: production
LOG_LEVEL: INFO
AUTH_SERVICE_URL: http://auth-service:8001
TASK_SERVICE_URL: http://task-service:8002
DATABASE_HOST: postgres
```

**Secrets**
```yaml
DATABASE_USER: postgres
DATABASE_PASSWORD: strong-password
SECRET_KEY: long-random-key-min-32-chars
GRAFANA_PASSWORD: secure-password
```

### Resource Limits

Per container:
- **Request**: CPU 100m, Memory 128Mi
- **Limit**: CPU 500m, Memory 512Mi

Total namespace:
- CPU: 4 cores
- Memory: 4Gi
- Pods: 20

Adjust in `09-resource-limits.yaml` based on cluster capacity.

### HPA Configuration

Services scale based on:
- CPU utilization > 70%
- Memory utilization > 80%

Min replicas: 2
Max replicas: 5

Configure in `11-hpa.yaml`.

## Deployment Workflow

### 1. Local Testing
```bash
# Build Dockerfile locally
docker build -f backend/services/auth-service/Dockerfile backend/services/auth-service

# Test docker-compose
docker-compose up
# Run smoke tests
curl http://localhost:8000/health
```

### 2. CI/CD Pipeline

Triggered on push to `main`:

```
Push to main
    ↓
Tests (auth, task, api-gateway, frontend)
    ↓
Lint (ruff for Python, eslint for JS)
    ↓
Build images (push to GHCR)
    ↓
Deploy to production
    ↓
Health checks
    ↓
Smoke tests
```

Workflows:
- `.github/workflows/backend-ci.yaml` - Test & build backend
- `.github/workflows/frontend-ci.yaml` - Test & build frontend
- `.github/workflows/deploy-prod.yaml` - Deploy to K8s

### 3. Manual Deployment

```bash
# 1. Build locally
docker build -t taskscheduler/auth-service:v1.0.0 backend/services/auth-service

# 2. Push to registry
docker push taskscheduler/auth-service:v1.0.0

# 3. Update K8s
kubectl set image deployment/auth-service \
  auth-service=taskscheduler/auth-service:v1.0.0 \
  -n taskscheduler

# 4. Monitor rollout
kubectl rollout status deployment/auth-service -n taskscheduler -w
```

## Monitoring & Debugging

### Check Pod Status
```bash
kubectl get pods -n taskscheduler
kubectl describe pod <pod-name> -n taskscheduler
kubectl logs <pod-name> -n taskscheduler
```

### Access Services
```bash
# Port forward
kubectl port-forward -n taskscheduler svc/api-gateway 8000:8000
curl http://localhost:8000/health

# Or use service DNS (from within cluster)
curl http://api-gateway:8000/health
```

### Database Access
```bash
# Connect via kubectl
kubectl exec -it postgres-0 -n taskscheduler -- \
  psql -U postgres -d taskscheduler

# Check migrations
SELECT * FROM alembic_version;

# Check migrations status
kubectl exec postgres-0 -n taskscheduler -- \
  psql -U postgres -d taskscheduler -c "SELECT * FROM alembic_version;"
```

### Prometheus
```bash
kubectl port-forward -n taskscheduler svc/prometheus 9090:9090
# Visit http://localhost:9090
# Query: up{job="auth-service"}
```

### Grafana
```bash
kubectl port-forward -n taskscheduler svc/grafana 3000:3000
# Visit http://localhost:3000
# Default: admin/admin (change password!)
```

## Scaling

### Horizontal Pod Autoscaling
- Configured in `11-hpa.yaml`
- Monitors CPU/memory
- Scales based on thresholds

Check HPA:
```bash
kubectl get hpa -n taskscheduler
kubectl describe hpa auth-service-hpa -n taskscheduler
```

### Manual Scaling
```bash
kubectl scale deployment auth-service --replicas=5 -n taskscheduler
```

### Database Scaling
- Single replica only (can add read replicas for reporting)
- Increase storage in `03-postgres.yaml`
- Adjust connection pool settings

## Backup & Recovery

### Database Backup
```bash
# Full backup
kubectl exec postgres-0 -n taskscheduler -- \
  pg_dump -U postgres taskscheduler > backup.sql

# Restore
kubectl exec -i postgres-0 -n taskscheduler -- \
  psql -U postgres taskscheduler < backup.sql
```

### Persistent Volume Backup
```bash
# Check PVC
kubectl get pvc -n taskscheduler

# Use your storage provider's backup mechanism
```

### Rollback Deployment
```bash
kubectl rollout history deployment/auth-service -n taskscheduler
kubectl rollout undo deployment/auth-service -n taskscheduler --to-revision=1
```

## Security Considerations

### Network Policies
- Default deny all traffic
- Whitelist only required connections (03-network-policies.yaml)

### Resource Limits
- Prevents resource exhaustion
- Protects against DoS

### Security Contexts
- Non-root users (runAsUser: 1000)
- Read-only root filesystem (where possible)
- Dropped Linux capabilities

### TLS/Certificates
- Update Ingress hostname in `08-ingress.yaml`
- Install cert-manager for auto TLS
- Use strong secrets

### Secrets Management
- Base64 encoded (not encrypted - add encryption at rest)
- Never commit to git
- Use external secret management (Sealed Secrets, HashiCorp Vault)

## Troubleshooting

### Pods not starting
```bash
kubectl describe pod <pod-name> -n taskscheduler
# Check: resource limits, image pull errors, health probe failures
```

### CrashLoopBackOff
```bash
# Check application logs
kubectl logs <pod-name> -n taskscheduler

# Common causes:
# - Database connection failed (wait for DB)
# - Migration failed (check DB schema)
# - Configuration missing (check ConfigMap/Secrets)
```

### High error rate
```bash
# Check Prometheus
kubectl port-forward svc/prometheus 9090:9090
# Query: rate(http_requests_total{status=~"5.."}[5m])

# Check logs
kubectl logs -f deployment/auth-service -n taskscheduler
```

### Slow queries
```bash
# Check database
kubectl exec postgres-0 -n taskscheduler -- \
  psql -U postgres -d taskscheduler \
  -c "SELECT query, mean_exec_time FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 5;"
```

### Storage full
```bash
# Check PVC usage
kubectl get pvc -n taskscheduler
kubectl describe pvc postgres-pvc -n taskscheduler

# Increase storage (depends on storage provider)
kubectl patch pvc postgres-pvc -n taskscheduler \
  -p '{"spec":{"resources":{"requests":{"storage":"20Gi"}}}}'
```

## Operations Runbook

### Weekly Tasks
- [ ] Check resource utilization
- [ ] Review error logs
- [ ] Monitor Prometheus/Grafana
- [ ] Test backup/recovery process

### Monthly Tasks
- [ ] Update dependencies
- [ ] Security patches
- [ ] Performance tuning
- [ ] Capacity planning

### Quarterly Tasks
- [ ] Load testing
- [ ] Disaster recovery drill
- [ ] Documentation update
- [ ] Architecture review

## Useful Commands

```bash
# Get all resources
kubectl get all -n taskscheduler

# Watch deployments
kubectl get deployment -n taskscheduler -w

# Get service endpoints
kubectl get endpoints -n taskscheduler

# Port forward multiple services
kubectl port-forward -n taskscheduler svc/api-gateway 8000:8000 &
kubectl port-forward -n taskscheduler svc/prometheus 9090:9090 &
kubectl port-forward -n taskscheduler svc/grafana 3000:3000 &

# SSH into pod
kubectl exec -it <pod-name> -n taskscheduler -- /bin/sh

# Follow logs
kubectl logs -f deployment/auth-service -n taskscheduler

# Get resource usage
kubectl top nodes
kubectl top pods -n taskscheduler
```

## Additional Resources
- K8s Deployment: `backend/services/k8s/README.md`
- Database Migrations: `backend/services/MIGRATION_GUIDE.md`
- GitHub Actions: `.github/workflows/`
- Docker Compose: `backend/services/docker-compose.yml`
