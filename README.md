# couchannel

Eksperymentalna platforma do wspólnego oglądania wydarzeń sportowych. Repo zawiera minimalny szkielet mikroserwisów w Pythonie/FastAPI i frontend React/Next.js gotowy do dalszego rozwoju.

## Struktura
- `services/api` – FastAPI gateway/BFF z przykładowym endpointem `GET /healthz`.
- `services/identity`, `services/inventory`, `services/booking` – minimalistyczne mikroserwisy z osobnymi kontraktami.
- `apps/web` – klient React (Vite + TypeScript) komunikujący się z API przez `/api` proxy.
- `contracts/` – OpenAPI 3.0 z definicjami interfejsów; aktualizuj przy każdej zmianie endpointów.
- `docker-compose.yml` – lokalna orkiestracja usług, używana przez Makefile.

## Jak uruchomić lokalnie
1. Zainstaluj Docker Desktop lub kompatybilny runtime.
2. Sklonuj repo i skopiuj `.env.example` do `.env`, aby ustawić domyślne adresy usług (`API_INVENTORY_URL`, `IDENTITY_REDIS_URL`, itp.).
3. W katalogu repo wykonaj `make compose-up` – zbuduje kontenery i wystartuje BFF (`localhost:8000`), mikroserwisy (`identity:8101`, `inventory:8102`, `booking:8103`), Postgresa (`localhost:5432`), Redisa (`localhost:6379`) oraz frontend (`localhost:5173`).
3. `inventory` automatycznie uruchamia Alembic (`alembic upgrade head`) przed startem, dzięki czemu tabela `events` i dane seedujące pojawiają się w bazie Postgres.
4. Po zmianach kodu usługi przeładują się automatycznie dzięki zamontowanym woluminom.
5. Zatrzymaj środowisko poleceniem `make compose-down`.

## Development bez Dockera
1. Utwórz wirtualne środowisko i zainstaluj `pip install -r requirements-dev.txt`.
2. Uruchom linting `make lint` (Ruff) i testy `make test` (wykorzystuje `./run-tests.sh`, który odpala dedykowany kontener `tests` z Pythonem 3.12 i uruchamia `pytest -vv`).
   - Aby dodać własne opcje, użyj `make test TEST_ARGS="tests/test_identity_profiles.py -k foo"` – zostaną przekazane do `pytest`.
3. Aby wykonać migracje na lokalnym Postgresie, przejdź do `services/inventory` i uruchom `alembic upgrade head` (wystarczy zmienna `INVENTORY_DATABASE_URL`).

## CI/CD i publikacja do GHCR
1. Workflow `.github/workflows/quality.yml` uruchamia `ruff check` i `pytest` przy każdym pushu/PR na `main`/`master`.
2. Aby publikować obrazy, ustaw sekrety `GHCR_USERNAME`/`GHCR_TOKEN` i pozostaw workflow `.github/workflows/docker-build.yml`, który buduje obrazy `api`, `identity`, `inventory`, `booking`, `web`. Push następuje dla gałęzi `main/master` do `ghcr.io/<owner>/couchchannel-<service>:latest`.

## Następne kroki
- Dodaj brokera zdarzeń (Kafka/Redpanda) i message-bus w Compose, aby `booking` mógł emitować eventy do `inventory`/`analytics`.
- Wprowadź autoryzację (OIDC) w `api` i `identity`, a następnie scenariusze e2e (Playwright) plus pipeline release (Helm + K8s).
