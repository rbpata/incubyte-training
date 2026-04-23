# TaskScheduler Architecture

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         INTERNET USERS                              │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                    ┌────────▼────────┐
                    │   Ingress/LB    │
                    │  (HTTPS 443)    │
                    └────────┬────────┘
                             │
                ┌────────────┼────────────┐
                │                         │
    ┌───────────▼──────────┐  ┌──────────▼──────────┐
    │ Frontend (nginx)     │  │  API Gateway        │
    │ - SPA (React+Vite)   │  │  (FastAPI:8000)    │
    │ - Static assets      │  │  - Routing          │
    │ - 2+ replicas        │  │  - CORS             │
    │ - Auto-scaling       │  │  - Logging          │
    └──────────────────────┘  │  - 2+ replicas      │
                              │  - Auto-scaling     │
                              └────────┬────────────┘
                                       │
                    ┌──────────────────┼──────────────────┐
                    │                  │                  │
        ┌───────────▼──────────┐ ┌────▼────────────┐    │
        │  Auth Service        │ │ Task Service    │    │
        │  (FastAPI:8001)      │ │ (FastAPI:8002)  │    │
        │  - Login/Logout      │ │ - CRUD ops      │    │
        │  - JWT tokens        │ │ - Data queries  │    │
        │  - 2+ replicas       │ │ - 2+ replicas   │    │
        │  - Auto-scaling      │ │ - Auto-scaling  │    │
        └───────────┬──────────┘ └────┬────────────┘    │
                    │                  │                  │
                    └──────────────────┼──────────────────┘
                                       │
                              ┌────────▼────────┐
                              │  PostgreSQL     │
                              │  (StatefulSet)  │
                              │  - 1 primary    │
                              │  - PVC (10GB)   │
                              │  - Migrations   │
                              └────────┬────────┘
                                       │
                ┌──────────────────────┴──────────────────────┐
                │                                             │
    ┌───────────▼──────────┐                   ┌────────────▼────────┐
    │    Prometheus        │                   │      Grafana        │
    │  - Metrics scraping  │                   │   - Dashboards      │
    │  - Alert rules       │                   │   - Alerting UI     │
    │  - 30s intervals     │                   │   - 2+ replicas     │
    │  - 30d retention     │                   │   - Auto-scaling    │
    └──────────────────────┘                   └─────────────────────┘
```

## Component Details

### Frontend Layer
- **Technology**: React 19 + Vite + TypeScript
- **Server**: nginx (alpine)
- **Build**: Multi-stage Docker build
- **Replicas**: 2 (minimum for HA)
- **Scaling**: HPA based on CPU/memory
- **Health Check**: GET /health → 200 OK

### API Gateway
- **Technology**: FastAPI with uvicorn
- **Port**: 8000
- **Responsibilities**:
  - Route requests to microservices
  - CORS handling
  - Request logging
  - Error handling
- **Replicas**: 2 (minimum for HA)
- **Scaling**: HPA (CPU >70%, Memory >80%)
- **Health Check**: GET /health → JSON response

### Auth Service
- **Technology**: FastAPI with uvicorn
- **Port**: 8001
- **Responsibilities**:
  - User authentication
  - JWT token generation/validation
  - Password hashing (bcrypt)
  - Session management
- **Database**: PostgreSQL (shared)
- **Replicas**: 2 (minimum for HA)
- **Scaling**: HPA (CPU >70%, Memory >80%)
- **Health Check**: GET /health → JSON response

### Task Service
- **Technology**: FastAPI with uvicorn
- **Port**: 8002
- **Responsibilities**:
  - Task CRUD operations
  - Task listing/filtering
  - Status management
  - User-specific queries
- **Database**: PostgreSQL (shared)
- **Replicas**: 2 (minimum for HA)
- **Scaling**: HPA (CPU >70%, Memory >80%)
- **Health Check**: GET /health → JSON response

### PostgreSQL
- **Technology**: PostgreSQL 16
- **Deployment**: StatefulSet (single pod)
- **Storage**: PersistentVolumeClaim (10GB)
- **Availability**: Single instance (upgrade to HA-DB if needed)
- **Connections**: Connection pooling (future optimization)
- **Backups**: Volume snapshots (depends on storage provider)

### Monitoring Stack
- **Prometheus**: Metrics collection, alerting
  - Scrape interval: 30s
  - Retention: 30 days
  - Alert rules: Service health, resource usage, DB health
  
- **Grafana**: Dashboards, visualization
  - Replicas: 2 (for HA)
  - Auto-scaling: Yes
  - Pre-configured datasource: Prometheus

## Network Architecture

### Kubernetes Network

```
┌─────────────────────────────────────┐
│     taskscheduler namespace         │
│  Subnet: 172.20.0.0/16              │
│                                     │
│  ┌─────────────────────────────┐   │
│  │ Services (ClusterIP)        │   │
│  │ - frontend:80               │   │
│  │ - api-gateway:8000          │   │
│  │ - auth-service:8001         │   │
│  │ - task-service:8002         │   │
│  │ - postgres:5432             │   │
│  │ - prometheus:9090           │   │
│  │ - grafana:3000              │   │
│  └─────────────────────────────┘   │
│                                     │
│  ┌─────────────────────────────┐   │
│  │ Network Policies            │   │
│  │ - Default deny all          │   │
│  │ - Allow required paths      │   │
│  │ - Service-to-service DNS    │   │
│  └─────────────────────────────┘   │
└─────────────────────────────────────┘
```

### Service-to-Service Communication

1. **Frontend → API Gateway**
   - HTTP requests to api-gateway:8000
   - REST endpoints

2. **API Gateway → Auth Service**
   - HTTP to auth-service:8001
   - Token validation, user lookup

3. **API Gateway → Task Service**
   - HTTP to task-service:8002
   - Task operations

4. **Services → PostgreSQL**
   - asyncpg connection pooling
   - Prepared statements

5. **Services → Prometheus**
   - Prometheus scrapes /metrics endpoints
   - 30 second intervals

## Data Flow

### User Request Flow

```
1. User browser → Frontend (nginx)
   └─ GET /
   └─ 200 + index.html

2. React app → API Gateway
   └─ POST /auth/login
   └─ API Gateway routes to Auth Service

3. Auth Service → PostgreSQL
   └─ Query user, validate password
   └─ Return JWT token

4. React app stores token

5. React app → API Gateway (with token)
   └─ GET /tasks
   └─ API Gateway routes to Task Service

6. Task Service → PostgreSQL
   └─ Query user's tasks
   └─ Return task list
```

### Monitoring Data Flow

```
1. Prometheus Scraper
   └─ Every 30 seconds
   └─ Scrape /metrics from all services

2. Services export metrics
   └─ HTTP requests (total, latency, errors)
   └─ Resource usage (CPU, memory)
   └─ Business metrics (tasks created, etc.)

3. Prometheus stores time-series data
   └─ Retention: 30 days

4. Grafana queries Prometheus
   └─ Displays dashboards
   └─ Renders graphs & alerts

5. Alert rules trigger
   └─ Prometheus evaluates rules
   └─ Sends notifications (if configured)
```

## Resource Allocation

### Compute Requests (Per container)
| Component | CPU | Memory |
|-----------|-----|--------|
| API Gateway | 100m | 128Mi |
| Auth Service | 100m | 128Mi |
| Task Service | 100m | 128Mi |
| Frontend | 50m | 64Mi |
| PostgreSQL | 250m | 256Mi |
| Prometheus | - | - |
| Grafana | - | - |

### Compute Limits (Per container)
| Component | CPU | Memory |
|-----------|-----|--------|
| API Gateway | 500m | 512Mi |
| Auth Service | 500m | 512Mi |
| Task Service | 500m | 512Mi |
| Frontend | 200m | 256Mi |
| PostgreSQL | 500m | 512Mi |
| Prometheus | - | - |
| Grafana | - | - |

### Storage
| Component | Type | Size |
|-----------|------|------|
| PostgreSQL PVC | PersistentVolume | 10Gi |
| Prometheus Data | emptyDir | Unlimited |
| Grafana Data | PersistentVolume | 5Gi |

## High Availability

### Pod Anti-Affinity
- Services prefer to run on different nodes
- Prevents single-node failure

### Health Checks
- **Liveness**: Restarts unhealthy pods
- **Readiness**: Removes unhealthy pods from service

### Resource Quotas
- Namespace limits: 4 cores CPU, 4Gi memory
- Prevents resource starvation

### Horizontal Scaling
- Configured auto-scaling for all stateless services
- Scales up/down based on CPU and memory utilization

### Database Resilience
- PVC ensures data persistence
- Volume snapshots for backups (depends on storage class)
- Connection retry logic in services

## Security

### Network Security
- Network policies restrict traffic
- Service-to-service communication via DNS

### Secrets Management
- Kubernetes Secrets for sensitive data
- Base64 encoding (add encryption at rest for production)

### Pod Security
- Non-root users (uid 1000)
- Read-only root filesystem (where possible)
- Dropped Linux capabilities

### RBAC
- Default service account (no elevated privileges)
- Cluster role bindings for required operations

## Scaling Topology

### Horizontal Scaling (Number of Replicas)
```
Min Replicas          Normal            Peak Load
─────────────────────────────────────────────────
Frontend: 2    ─ 2-3 ─────────── 3 (max)
API GW:   2    ─ 2-3 ─────────── 5 (max)
Auth:     2    ─ 2-3 ─────────── 5 (max)
Task:     2    ─ 2-3 ─────────── 5 (max)
DB:       1 ────────────────────── 1 (single primary)
```

### Vertical Scaling (Resource Limits)
- Increase CPU/memory limits in ResourceQuota
- Requires cluster resources available
- May require node scaling

## Deployment Strategies

### Rolling Update
- Default strategy
- Gradual pod replacement
- Zero downtime
- Automatic rollback on failure

### Blue-Green (Future)
- Maintain two production environments
- Switch traffic between versions
- Faster rollback

### Canary (Future)
- Gradually route traffic to new version
- Monitor metrics before full rollout
- Automatic rollback if errors

## Future Enhancements

1. **Database HA**
   - Primary + standby replicas
   - Automated failover

2. **Distributed Caching**
   - Redis for session/cache layer
   - Improves performance

3. **Event Queue**
   - Message broker (RabbitMQ/Kafka)
   - Async task processing

4. **Search**
   - Elasticsearch for full-text search
   - Task search optimization

5. **CDN**
   - Frontend assets via CDN
   - Faster global delivery

6. **Multi-region**
   - Replicate services across regions
   - Active-active setup
   - Global load balancing
