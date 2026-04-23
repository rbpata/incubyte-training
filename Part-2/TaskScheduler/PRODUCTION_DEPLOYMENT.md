# TaskScheduler - Production Deployment Complete

Complete production-ready deployment pipeline for TaskScheduler with Docker, Kubernetes, CI/CD, and monitoring.

## 📦 What's Included

### Containerization
- **Multi-stage Dockerfiles** for all services
- Optimized images with security best practices
- Health checks & non-root users
- Services: Frontend, API Gateway, Auth Service, Task Service

### Docker Compose
- Full local development stack
- PostgreSQL + Prometheus + Grafana
- Pre-configured networking and health checks
- Environment variable management

### Kubernetes
- 13 manifest files for production deployment
- StatefulSet for PostgreSQL
- Deployments with HPA (Horizontal Pod Autoscaling)
- Ingress, NetworkPolicies, ResourceQuotas
- Database migration job

### CI/CD Pipeline
- GitHub Actions workflows
- Automated testing (pytest, vitest)
- Linting (ruff, eslint)
- Docker image building & publishing
- Automated deployment on main branch
- Rollback support

### Monitoring
- Prometheus for metrics collection
- Grafana dashboards
- Alert rules for health, latency, errors, resources
- Service health checks

### Documentation
- Comprehensive deployment guide (DEPLOYMENT.md)
- Detailed architecture documentation (ARCHITECTURE.md)
- Kubernetes deployment guide (k8s/README.md)
- Database migration guide (MIGRATION_GUIDE.md)

## 🚀 Quick Start

### Local Development with Docker Compose
```bash
cd backend/services
cp .env.example .env
docker-compose up -d

# Verify
docker-compose ps
curl http://localhost:8000/health

# Access
Frontend:    http://localhost
API:         http://localhost:8000
Grafana:     http://localhost:3001 (admin/admin)
Prometheus:  http://localhost:9090
```

### Production Deployment with Kubernetes
```bash
cd backend/services/k8s

# Deploy infrastructure
kubectl apply -f 00-namespace.yaml
kubectl apply -f 01-configmap.yaml
kubectl apply -f 02-secrets.yaml
kubectl apply -f 03-postgres.yaml

# Wait for database
kubectl wait --for=condition=ready pod -l app=postgres -n taskscheduler --timeout=120s

# Run migrations
kubectl apply -f 12-db-migration.yaml
kubectl wait --for=condition=complete job/db-migration -n taskscheduler --timeout=60s

# Deploy services
kubectl apply -f 04-auth-service.yaml
kubectl apply -f 05-task-service.yaml
kubectl apply -f 06-api-gateway.yaml
kubectl apply -f 07-frontend.yaml

# Deploy infrastructure
kubectl apply -f 08-ingress.yaml
kubectl apply -f 09-resource-limits.yaml
kubectl apply -f 10-network-policies.yaml
kubectl apply -f 11-hpa.yaml

# Verify
kubectl get all -n taskscheduler
```

## 📋 File Structure

```
TaskScheduler/
├── .github/workflows/
│   ├── backend-ci.yaml          # Test, lint, build backend
│   ├── frontend-ci.yaml         # Test, lint, build frontend
│   └── deploy-prod.yaml         # Deploy to production
│
├── backend/services/
│   ├── auth-service/
│   │   └── Dockerfile           # Multi-stage build
│   ├── task-service/
│   │   └── Dockerfile
│   ├── api-gateway/
│   │   └── Dockerfile
│   ├── k8s/                      # Kubernetes manifests
│   │   ├── 00-namespace.yaml
│   │   ├── 01-configmap.yaml
│   │   ├── 02-secrets.yaml
│   │   ├── 03-postgres.yaml
│   │   ├── 04-auth-service.yaml
│   │   ├── 05-task-service.yaml
│   │   ├── 06-api-gateway.yaml
│   │   ├── 07-frontend.yaml
│   │   ├── 08-ingress.yaml
│   │   ├── 09-resource-limits.yaml
│   │   ├── 10-network-policies.yaml
│   │   ├── 11-hpa.yaml
│   │   ├── 12-db-migration.yaml
│   │   └── README.md            # K8s deployment guide
│   ├── prometheus/
│   │   ├── prometheus.yml       # Enhanced config
│   │   └── alert-rules.yml      # Alert definitions
│   ├── grafana/
│   │   ├── provisioning/
│   │   │   ├── datasources/
│   │   │   │   └── prometheus.yml
│   │   │   └── dashboards/
│   │   │       └── default.yml
│   │   └── dashboards/
│   │       └── services.json    # Service dashboard
│   ├── docker-compose.yml       # Local dev stack
│   ├── .env.example             # Environment template
│   ├── entrypoint.sh            # Migration + app startup
│   └── MIGRATION_GUIDE.md       # Database migrations
│
├── frontend/
│   ├── Dockerfile              # Multi-stage nginx build
│   └── nginx.conf              # SPA routing config
│
├── DEPLOYMENT.md               # Production deployment guide
├── ARCHITECTURE.md             # Architecture documentation
└── README.md                   # This file
```

## 🏗️ Architecture

```
                    Internet
                       ↓
                   [Ingress/LB]
                    ↙    ↓    ↘
            [Frontend]  [API]  
                        ↙ ↘
                    [Auth] [Task]
                        ↘ ↙
                    [PostgreSQL]
                        ↓
                [Prometheus + Grafana]
```

**Key Features:**
- ✅ High availability (2+ replicas per service)
- ✅ Horizontal scaling (auto-scale to 5 replicas)
- ✅ Health checks (liveness + readiness probes)
- ✅ Resource limits & quotas
- ✅ Network policies (security)
- ✅ Automated migrations
- ✅ Monitoring & alerts
- ✅ Blue-green deployment support

## 🔧 Configuration

### Environment Variables

**ConfigMap** (application config):
```yaml
ENVIRONMENT: production
LOG_LEVEL: INFO
AUTH_SERVICE_URL: http://auth-service:8001
TASK_SERVICE_URL: http://task-service:8002
```

**Secrets** (sensitive data):
```yaml
DATABASE_USER: postgres
DATABASE_PASSWORD: secure-password
SECRET_KEY: long-random-key
GRAFANA_PASSWORD: secure-password
```

Edit in Kubernetes:
```bash
kubectl edit configmap taskscheduler-config -n taskscheduler
kubectl edit secret taskscheduler-secrets -n taskscheduler
```

## 📊 Monitoring

### Prometheus Metrics
- Service health (up/down)
- Request rate & latency
- Error rate
- Database connections
- Resource usage (CPU/memory)

### Grafana Dashboards
- Service status
- Request metrics
- Error tracking
- Database health
- Cache performance

### Alerts
- High error rate
- Service down
- High latency
- High resource usage
- Low disk space

Access:
```bash
# Prometheus
kubectl port-forward -n taskscheduler svc/prometheus 9090:9090

# Grafana
kubectl port-forward -n taskscheduler svc/grafana 3000:3000
# Login: admin/admin (change password!)
```

## 🚢 Deployment

### GitHub Actions CI/CD

**Trigger:** Push to main branch

**Pipeline:**
1. Run tests (pytest, vitest)
2. Lint code (ruff, eslint)
3. Build Docker images
4. Push to GHCR (GitHub Container Registry)
5. Deploy to Kubernetes
6. Run health checks
7. Smoke tests

### Manual Deployment

```bash
# Build locally
docker build -t taskscheduler/auth-service:v1.0.0 backend/services/auth-service

# Push to registry
docker push taskscheduler/auth-service:v1.0.0

# Update Kubernetes
kubectl set image deployment/auth-service \
  auth-service=taskscheduler/auth-service:v1.0.0 \
  -n taskscheduler

# Monitor rollout
kubectl rollout status deployment/auth-service -n taskscheduler -w
```

## 📚 Documentation

- **DEPLOYMENT.md** - Complete deployment & operations guide
- **ARCHITECTURE.md** - System design, data flows, components
- **backend/services/k8s/README.md** - Kubernetes specifics
- **backend/services/MIGRATION_GUIDE.md** - Database migrations
- **backend/services/.env.example** - Configuration template

## 🔒 Security

- Non-root users (uid 1000)
- Read-only root filesystems (where possible)
- Network policies (default deny)
- Resource quotas
- Secrets management
- TLS/HTTPS (via cert-manager)
- Security contexts (dropped capabilities)

## 📈 Scaling

### Automatic (HPA)
- Scales 2-5 replicas based on CPU/memory
- Configured in `11-hpa.yaml`

### Manual
```bash
kubectl scale deployment auth-service --replicas=10 -n taskscheduler
```

## 🔄 Rollback

```bash
# View history
kubectl rollout history deployment/auth-service -n taskscheduler

# Rollback to previous version
kubectl rollout undo deployment/auth-service -n taskscheduler

# Rollback to specific revision
kubectl rollout undo deployment/auth-service --to-revision=2 -n taskscheduler
```

## 🛠️ Troubleshooting

### Pod not starting
```bash
kubectl describe pod <pod-name> -n taskscheduler
kubectl logs <pod-name> -n taskscheduler
```

### Database connection issues
```bash
kubectl exec postgres-0 -n taskscheduler -- \
  psql -U postgres -d taskscheduler -c "SELECT * FROM alembic_version;"
```

### High error rate
```bash
# Check Prometheus
kubectl port-forward -n taskscheduler svc/prometheus 9090:9090
# Query: rate(http_requests_total{status=~"5.."}[5m])

# Check logs
kubectl logs -f deployment/auth-service -n taskscheduler
```

See **DEPLOYMENT.md** for comprehensive troubleshooting.

## 📦 Dependencies

### Backend
- Python 3.12
- FastAPI, uvicorn
- PostgreSQL, asyncpg
- pytest, ruff

### Frontend
- Node.js 22
- React 19, Vite
- TypeScript, pnpm
- Vitest, eslint

### Deployment
- Docker & Docker Compose
- Kubernetes 1.28+
- kubectl
- Git & GitHub Actions

## 📝 Next Steps

1. Update `backend/services/.env` with your configuration
2. Update `backend/services/k8s/02-secrets.yaml` with production secrets
3. Update `backend/services/k8s/08-ingress.yaml` with your domain
4. Install cert-manager for TLS
5. Create GitHub secrets for deployment (KUBE_CONFIG)
6. Push to main branch to trigger CI/CD

## 📞 Support

- See **DEPLOYMENT.md** for operations guide
- See **ARCHITECTURE.md** for design details
- Check GitHub Actions logs for CI/CD issues
- Review Kubernetes events: `kubectl describe pod <name> -n taskscheduler`

---

**Ready for production deployment!** 🚀
