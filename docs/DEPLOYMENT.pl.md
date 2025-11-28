# Deployment plan

## Helm & Kubernetes
- Package each microservice as a container (already produced by GitHub Actions) and publish to GHCR: `ghcr.io/<owner>/couchannel-<service>:<tag>`.
- Create Helm charts under `deploy/helm/<service>` with templates for Deployment, Service, ConfigMap (env vars), and horizontal pod autoscaling hints.
- Compose them via umbrella chart (`deploy/helm/couchannel`) wiring in Postgres (RDS) and Redis (Elasticache) or their managed equivalents.
- Use Istio or Linkerd for mTLS + traffic shaping (canary releases). Ingress routes web traffic via API gateway; identity/booking/inventory remain cluster-internal.
- CI pipeline: build + push images → `helm lint` → render manifests → deploy to staging cluster using `helm upgrade --install` with a GitHub Actions environment requiring manual approval for production.

## Secrets & Config
- Enforce secret storage in HashiCorp Vault or AWS Secrets Manager; inject via CSI driver or ExternalSecrets.
- For OIDC, configure an external provider (Auth0/Keycloak) and point `API_OIDC_*` env vars accordingly.
- Kafka (Redpanda) can run as a StatefulSet with persistence; for production consider managed Kafka (Confluent/AWS MSK) and update bootstrap URLs.

## Release workflow
1. Developer opens PR → `quality.yml` runs lint/tests.
2. Merge to `main` triggers `docker-build.yml`, pushing `latest` images.
3. Git tag (e.g., `v0.2.0`) triggers release workflow: downloads Helm values, substitutes image tags, deploys to staging using GitHub OIDC → cloud credentials.
4. After smoke tests (Playwright) succeed, manually approve promotion job to apply Helm chart to production namespace.
