# couchannel architecture (EN)

_See also the Polish version: [`ARCHITECTURE.pl.md`](ARCHITECTURE.pl.md)._ 

## Bounded contexts & services
- **Identity & Reputation** – authentication/token issuance, host reputation, future KYC/AML hooks. Uses Postgres + Redis.
- **Host & Venue Management** – `inventory-service` (viewing sessions, availability), `pricing-service` (dynamic price), storage for host media.
- **Discovery & Engagement** – search/read models (Elasticsearch), notification, reviews/analytics.
- **Transactions** – `booking-service` (Saga orchestrator), payments/payouts/compliance, analytics.

## Key patterns
- **API Gateway + BFF** – FastAPI edge service exposes REST, aggregates data for web/mobile BFFs, enforces throttling, feature flags, auth.
- **Service Discovery & Config** – environment variables + Vault/Dynaconf; plan for Consul/Eureka when the platform grows.
- **Event-driven communication** – Kafka/Redpanda domain events. Booking publishes `booking.events`, inventory consumes and updates availability. Critical flows will adopt Outbox + Event Sourcing.
- **Saga/Choreography** – Booking orchestrates inventory, pricing, payment, compliance; compensating transactions release seats/refunds on failure.
- **CQRS** – write models in Postgres, read models (search, dashboards) materialized via Kafka consumers.
- **Observability** – OpenTelemetry + Prometheus/Grafana/Tempo; every service exposes `/healthz`, `/readinessz`, and propagates trace IDs.
- **Security** – API Gateway applies rate limiting, retries, idempotency, mTLS via service mesh (Istio/Linkerd). Per-tenant isolation planned for enterprise edition. OIDC demo issuer is built-in for dev.

## Critical flows
1. Guest searches sessions → API Gateway hits inventory read model → BFF decorates with host profile + price.
2. Booking reserves seats → emits `BookingInitiated` → Saga locks slots, calls pricing/payment/compliance.
3. Compliance validates league rules and attendee count → Booking emits `BookingConfirmed` → Notifications inform host/guest.
4. After the session, review service records ratings, analytics aggregates NPS and subscription usage.

## Data stores
- Relational (users, payments, viewing sessions) → Postgres + migrations (Alembic/Flyway).
- Read-heavy workloads → Elasticsearch, Redis caches, potential Rockset/BQ mirrors.
- Telemetry → Loki/Tempo, metrics in Prometheus/Mimir, Kafka log as source-of-truth for asynchronous replicators.

## Tech stack & delivery
- Backend services: Python 3.12 + FastAPI, Pydantic v2, SQLModel/SQLAlchemy, async workers (Celery/Dramatiq). gRPC/Protobuf for low-latency sync calls.
- Frontends: React 18 + Next.js (SSR) and React Native; data fetched via GraphQL/REST from BFF.
- Containers packaged with Docker; Helm charts under `deploy/helm`. EKS/GKE + Istio for blue/green or canary releases.
- CI/CD: GitHub Actions running lint/tests, Docker builds, security scans (Snyk/Trivy), promotion pipeline with manual approval.
- Local dev: `make compose-up` runs Postgres, Redis, Redpanda (Kafka), gateway + services + web via Docker Compose; contracts tracked in `contracts/` (OpenAPI/AsyncAPI).

## Repository workflow
- Work locally (Docker Desktop + `docker compose up`), but structure is ready to push to GitHub/CI.
- Compose already bundles critical dependencies (Postgres, Redis, Redpanda). Add Temporal or extra brokers via separate compose profiles when needed.
- Per-service `.env` stays local; commit `.env.example` only. Secrets for cloud go into Vault/Secret Manager.
- Keep `main` releasable; feature branch → PR → GitHub Actions (quality check + optional image push).
- For remote clusters (k3d/kind/EKS), reuse the Helm chart from `deploy/helm` and promote via GitHub Actions environments.
