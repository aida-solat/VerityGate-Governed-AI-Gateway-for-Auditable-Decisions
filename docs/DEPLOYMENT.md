# Deployment Guide

> Built & designed by **Deciwa**.

This guide covers deploying VerityGate to production on **AWS ECS/Fargate** or
**Azure Container Apps**, with managed Postgres (pgvector), Redis, and the
full observability stack.

---

## Prerequisites

- Docker and Docker Compose (local testing)
- Terraform >= 1.5
- AWS CLI or Azure CLI (depending on target cloud)
- GitHub repository with Actions enabled
- Container registry (GHCR is preconfigured in CI; ECR/ACR for cloud-native)

---

## Local (docker-compose)

The fastest way to run the full production-like stack locally:

```bash
docker compose up --build
```

This starts:
- **Backend** on `http://localhost:8009` (Postgres, Redis, OTEL enabled)
- **Frontend** on `http://localhost:3009`
- **Postgres + pgvector** on port 5432
- **Redis** on port 6379
- **OTEL Collector** → Prometheus metrics
- **Prometheus** on `http://localhost:9090`
- **Grafana** on `http://localhost:3000` (admin/admin, auto-provisioned dashboard)

---

## AWS ECS/Fargate

### 1. Create ECR repository

```bash
aws ecr create-repository --repository-name veritygate-backend
```

### 2. Build and push image

```bash
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
docker build -t veritygate-backend ./backend
docker tag veritygate-backend:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/veritygate-backend:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/veritygate-backend:latest
```

### 3. Deploy infrastructure with Terraform

```bash
cd infra/aws
terraform init
terraform plan -var="db_password=<secure-password>" -var="ecr_repo_url=<account-id>.dkr.ecr.us-east-1.amazonaws.com/veritygate-backend"
terraform apply
```

This creates:
- VPC with public/private subnets + NAT
- RDS Postgres 16 (pgvector-compatible)
- ElastiCache Redis 7.2
- ECS Fargate cluster + service (2 tasks, ALB)
- CloudWatch log group

### 4. Verify

```bash
curl http://$(terraform output -raw alb_dns)/health
# {"status": "ok"}
```

### 5. Enable pgvector extension

Connect to RDS and run:
```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

---

## Azure Container Apps

### 1. Create Container Registry

```bash
az acr create --name veritygate --resource-group veritygate-rg --sku Basic
az acr login --name veritygate
```

### 2. Build and push image

```bash
docker build -t veritygate.azurecr.io/veritygate-backend ./backend
docker push veritygate.azurecr.io/veritygate-backend:latest
```

### 3. Deploy infrastructure with Terraform

```bash
cd infra/azure
terraform init
terraform plan -var="db_password=<secure-password>" -var="acr_login_server=veritygate.azurecr.io"
terraform apply
```

This creates:
- Resource group
- Azure Database for PostgreSQL Flexible Server (pgvector enabled)
- Azure Cache for Redis
- Log Analytics workspace
- Container App Environment + backend app (auto-scaling 1–5 replicas)

### 4. Verify

```bash
curl https://$(terraform output -raw backend_url)/health
# {"status": "ok"}
```

---

## CI/CD (GitHub Actions)

The workflow (`.github/workflows/ci.yml`) runs automatically:

1. **On pull request**: run pytest + frontend lint/build.
2. **On push to main**: build Docker images → push to GHCR → deploy.

To enable deployment:
1. Set repository secrets: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` (AWS) or `AZURE_CREDENTIALS` (Azure).
2. Uncomment the relevant deploy step in the workflow.
3. Push to `main`.

---

## Observability

### Prometheus metrics

The backend exposes `/metrics` (Prometheus text format) with:
- `veritygate_requests_total` (by provider, risk_level)
- `veritygate_gate_outcomes_total` (by status)
- `veritygate_eval_failures_total` (by check)
- `veritygate_cache_hits_total`
- `veritygate_cost_usd_total` (by provider)
- `veritygate_latency_ms` (histogram)

### Grafana

Auto-provisioned dashboard at `http://localhost:3000` (docker-compose) showing:
- Requests/min by provider
- Gate outcomes/min
- P95 latency
- Cumulative cost
- Cache hit rate
- Eval failures

### OpenTelemetry traces

When `OTEL_ENABLED=true`, distributed traces cover:
- FastAPI request handling
- SQLAlchemy queries
- httpx provider calls
- Redis cache operations

Traces export via OTLP gRPC to the collector. Plug in Jaeger, Tempo, or any
OTLP-compatible backend.

---

## Environment variables (production)

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | yes | `postgresql+psycopg://user:pass@host/db` |
| `REDIS_URL` | yes | `redis://host:6379/0` or `rediss://` for TLS |
| `OTEL_ENABLED` | no | `true` to enable tracing |
| `OTEL_EXPORTER_ENDPOINT` | no | OTLP gRPC endpoint (default `localhost:4317`) |
| `OPENAI_API_KEY` | no | Enables OpenAI provider |
| `ANTHROPIC_API_KEY` | no | Enables Anthropic provider |
| `USE_LLM_JUDGE` | no | `true` to enable LLM-as-judge scoring |
| `ROUTING_STRATEGY` | no | `risk` / `cost` / `latency` / `quality` |
| `ENVIRONMENT` | no | `production` / `development` |

---

## Security hardening checklist

- [ ] TLS termination at ALB/ingress (HTTPS only)
- [ ] Secrets in AWS Secrets Manager / Azure Key Vault (not env vars in task def)
- [ ] Database connections via private subnet only
- [ ] Redis AUTH enabled + TLS (`rediss://`)
- [ ] Container runs as non-root user
- [ ] Enable GitHub Dependabot + container scanning
- [ ] Review [THREAT_MODEL.md](THREAT_MODEL.md)

---

Built & designed by **Deciwa**.
