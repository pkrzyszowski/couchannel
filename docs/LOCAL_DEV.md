# Local development (EN)

_Polish instructions: [`LOCAL_DEV.pl.md`](LOCAL_DEV.pl.md)._ 

## Requirements
- Docker Desktop or compatible runtime.
- Node.js 20+ (optional, only if you want to run the web client outside Docker).
- Python 3.12 (optional, for running lint/tests without containers).

## Getting started
1. `cp .env.example .env` – provides default URLs, Kafka settings, Redis/Postgres credentials.
2. `make compose-up` – spins up Postgres, Redis, Redpanda (Kafka), API gateway, identity/inventory/booking, web, plus Prometheus (`http://localhost:9090`) and Grafana (`http://localhost:3000`).
3. Visit `http://localhost:5173` (web) and `http://localhost:8000` (API). Inventory auto-runs Alembic and seeds demo viewing sessions; booking writes into the same Postgres instance (`booking_records` table) when you hit `POST /bookings`; analytics exposes aggregates under `http://localhost:8104/stats`.
4. Stop everything with `make compose-down` (add `-v` to drop Postgres volume).

## Useful commands
- `make lint` – runs Ruff locally.
- `make test` / `./run-tests.sh` – builds the `tests` container (Python 3.12), installs `requirements-dev.txt`, and executes `pytest -vv`. Kafka/auth are disabled inside the container via env vars; pass extra flags via `TEST_ARGS`.
- `docker compose logs -f <service>` – tail logs for debugging.
- `docker compose exec db psql -U couchchannel -d couchchannel` – inspect Postgres.
- `docker compose exec inventory alembic revision --autogenerate -m "message"` – generate new migrations (ensure env vars are set).

## Troubleshooting
- **Identity/Redis issues** – ensure `IDENTITY_REDIS_URL` matches Docker Compose (redis service). Restart container if flush fails.
- **Inventory not starting** – check logs; Redpanda or Postgres might still be initialising. Compose already declares dependencies, but you can add a short `sleep` or `wait-for-it` if needed.
- **Metrics not visible** – ensure services expose `/metrics` (handled by `prometheus-fastapi-instrumentator`). Prometheus UI lives at `http://localhost:9090`, Grafana at `http://localhost:3000` with anonymous viewer role.
- **Frontend shows "Unable to reach API"** – confirm API runs on port 8000 and `/api` proxy rewrites (`apps/web/vite.config.ts`).
- **Tests can't import modules** – run via `make test` (Docker container) or set `PYTHONPATH=$(pwd)` before `pytest` locally.
