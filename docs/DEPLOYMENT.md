# Deployment plan (EN)

_Polish version: [`DEPLOYMENT.pl.md`](DEPLOYMENT.pl.md)._ 

## Helm & Kubernetes
- Build/push images via GitHub Actions (`docker-build.yml`) to `ghcr.io/<owner>/couchannel-<service>:<tag>`.
- Create per-service Helm charts under `deploy/helm/<service>`: Deployment, Service, ConfigMap/Secret templates, HPA hints.
- Use an umbrella chart (`deploy/helm/couchannel`) to wire Postgres (RDS/Aurora), Redis (Elasticache), Redpanda/Kafka (Managed MSK/Confluent), and the API/web ingress.
- Service mesh (Istio/Linkerd) enforces mTLS and traffic shifting (canary/blue-green). API gateway behind ingress, internal services cluster-only.
- CI flow: build images → `helm lint` → render manifests → `helm upgrade --install` to staging cluster via GitHub OIDC → cloud credentials. Production promotion requires manual approval in Actions Environments.

## Secrets & Configuration
- Store secrets in Vault or AWS Secrets Manager; sync via ExternalSecrets/CSI driver. Never check `.env` with credentials.
- Integrate with a managed OIDC provider (Auth0/Keycloak/AWS Cognito) and point `API_OIDC_*` env vars accordingly (current RSA key is demo-only).
- Kafka: run Redpanda as StatefulSet with persistence or switch to managed Kafka (Confluent Cloud / AWS MSK). Update `*_KAFKA_BOOTSTRAP` env vars accordingly.

## Release workflow
1. Developer opens PR → `quality.yml` (lint/tests) must pass.
2. Merge to `main` triggers `docker-build.yml` (images pushed to GHCR if secrets are present).
3. Tag release (`v0.x.y`) → release workflow fetches Helm values, substitutes image tags, deploys to staging cluster.
4. Playwright e2e suite runs against staging; on success, manual approval promotes chart to production namespace.

## Future enhancements
- Add automated database migrations (e.g., `alembic upgrade`) as init containers in Helm charts.
- Integrate observability stack (Prometheus, Grafana, Tempo) via Helm dependencies.
- Use ArgoCD/Flux for GitOps if you prefer pull-based deployments instead of GitHub Actions push.
