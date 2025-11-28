# couchannel

Couchannel is a BlaBlaCar-style platform for shared sports-stream sessions: hosts open their living rooms + streaming packages so guests can split subscription costs. This repo contains a minimal microservice skeleton (FastAPI, React, Docker Compose) ready to demo to recruiters or evolve into a full product. (Polish version: [`README.pl.md`](README.pl.md))

## Structure
- `services/api` – FastAPI gateway/BFF with `/healthz` and `/events/aggregated` that fans out to downstream services.
- `services/identity`, `services/inventory`, `services/booking` – domain microservices with their own Dockerfiles and OpenAPI specs; booking publishes Kafka events, inventory consumes them.
- `apps/web` – React (Vite + TypeScript) frontend that proxies to the API via `/api`.
- Frontend obtains a demo bearer token via `POST /api/auth/token` (gateway proxies to Identity) and uses it against `/api/events/aggregated`.
- `contracts/` – OpenAPI 3.0 specifications, source of truth for interfaces.
- `docker-compose.yml` – orchestrates Postgres, Redis, microservices, and frontend.

## Local run
1. Install Docker Desktop (or any compatible runtime).
2. Clone the repo and copy `.env.example` to `.env` (default service URLs and credentials).
3. Run `make compose-up` – builds containers and starts the gateway (`localhost:8000`), microservices (`identity:8101`, `inventory:8102`, `booking:8103`), Postgres (`localhost:5432`), Redis (`localhost:6379`), and web (`localhost:5173`).
4. Inventory runs Alembic (`alembic upgrade head`) on startup, seeding demo events into Postgres.
5. Redpanda (Kafka-compatible) powers the booking event stream; containers auto-create the `booking.events` topic.
6. Hot reload is enabled via bind mounts. Stop everything with `make compose-down` (add `-v` to drop DB data).

## Development workflow
1. Optional: `pip install -r requirements-dev.txt` (if you want to run lint/tests locally without Docker).
2. `make lint` runs Ruff; `make test` uses `./run-tests.sh` to spin up the `tests` container (Python 3.12), install dev deps, and execute `pytest -vv`. Pass custom args via `make test TEST_ARGS="tests/test_identity_profiles.py -k foo"`.
3. To run Alembic migrations manually, `cd services/inventory && alembic upgrade head` (ensure `INVENTORY_DATABASE_URL` is set).

## Auth & event bus quickstart
- Request a demo token via `POST /api/auth/token` (the gateway proxies to Identity) and use it as `Authorization: Bearer <token>` when hitting `/api/events/aggregated`.
- Booking emits JSON events to the `booking.events` Kafka topic (Redpanda). Inventory consumes them and decrements `slots_available` for the matching event ID. Inspect activity with `docker compose logs booking inventory redpanda -f`.

## CI/CD, e2e & publishing
1. `.github/workflows/quality.yml` runs Ruff + pytest on every push/PR to `main`/`master`.
2. `.github/workflows/docker-build.yml` builds (and optionally pushes) Docker images for `api`, `identity`, `inventory`, `booking`, `web`. Configure `GHCR_USERNAME`/`GHCR_TOKEN` with `workflow` scope to push to `ghcr.io/<owner>/couchannel-<service>:latest`.
3. End-to-end scaffolding lives in `e2e/` (Playwright). Run `cd e2e && npm install && npx playwright test` against a running `make compose-up` stack.
4. See `docs/DEPLOYMENT.md` for the Helm/Kubernetes release plan (GH Actions → Helm upgrade with manual approvals).

## Next steps
- Enrich booking saga with payments/compliance, extend event payloads, and plug analytics-service consumers.
- Connect to a managed OIDC provider (Auth0/Keycloak) instead of the built-in demo issuer, then follow `docs/DEPLOYMENT.md` to push Helm charts onto a managed Kubernetes cluster.
