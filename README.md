# couchannel

Couchannel is a BlaBlaCar-style platform for shared sports-stream sessions: hosts open their living rooms + streaming packages so guests can split subscription costs. This repo contains a minimal microservice skeleton (FastAPI, React, Docker Compose) ready to demo to recruiters or evolve into a full product.

## Structure
- `services/api` – FastAPI gateway/BFF with `/healthz` and `/events/aggregated` that fans out to downstream services.
- `services/identity`, `services/inventory`, `services/booking` – domain microservices with their own Dockerfiles and OpenAPI specs.
- `apps/web` – React (Vite + TypeScript) frontend that proxies to the API via `/api`.
- `contracts/` – OpenAPI 3.0 specifications, source of truth for interfaces.
- `docker-compose.yml` – orchestrates Postgres, Redis, microservices, and frontend.

## Local run
1. Install Docker Desktop (or any compatible runtime).
2. Clone the repo and copy `.env.example` to `.env` (default service URLs and credentials).
3. Run `make compose-up` – builds containers and starts the gateway (`localhost:8000`), microservices (`identity:8101`, `inventory:8102`, `booking:8103`), Postgres (`localhost:5432`), Redis (`localhost:6379`), and web (`localhost:5173`).
4. Inventory runs Alembic (`alembic upgrade head`) on startup, seeding demo events into Postgres.
5. Hot reload is enabled via bind mounts. Stop everything with `make compose-down` (add `-v` to drop DB data).

## Development workflow
1. Optional: `pip install -r requirements-dev.txt` (if you want to run lint/tests locally without Docker).
2. `make lint` runs Ruff; `make test` uses `./run-tests.sh` to spin up the `tests` container (Python 3.12), install dev deps, and execute `pytest -vv`. Pass custom args via `make test TEST_ARGS="tests/test_identity_profiles.py -k foo"`.
3. To run Alembic migrations manually, `cd services/inventory && alembic upgrade head` (ensure `INVENTORY_DATABASE_URL` is set).

## CI/CD & publishing
1. `.github/workflows/quality.yml` runs Ruff + pytest on every push/PR to `main`/`master`.
2. `.github/workflows/docker-build.yml` builds (and optionally pushes) Docker images for `api`, `identity`, `inventory`, `booking`, `web`. Configure `GHCR_USERNAME`/`GHCR_TOKEN` with `workflow` scope to push to `ghcr.io/<owner>/couchannel-<service>:latest`.

## Next steps
- Add an event broker (Kafka/Redpanda) so `booking` emits domain events consumed by `inventory`/`analytics`.
- Introduce OIDC auth in `api`/`identity`, plus end-to-end scenarios (Playwright) and a release pipeline (Helm + Kubernetes).
