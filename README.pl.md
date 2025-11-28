# couchannel (PL)

couchannel to koncepcja w stylu BlaBlaCar, ale dla wspólnego oglądania sportu: gospodarze udostępniają salon + abonamenty, a goście współdzielą koszt. Repozytorium zawiera szkielet mikroserwisów (FastAPI, React, Docker Compose) gotowy do zaprezentowania rekruterom.

## Struktura
- `services/api` – FastAPI gateway/BFF z endpointami `/healthz` oraz `/events/aggregated` agregującymi dane z innych serwisów.
- `services/identity`, `services/inventory`, `services/booking` – serwisy domenowe z własnymi Dockerfile i kontraktami; booking publikuje zdarzenia Kafka, inventory je konsumuje.
- `apps/web` – frontend React (Vite + TS) komunikujący się z API przez `/api`.
- `contracts/` – specyfikacje OpenAPI, źródło prawdy dla interfejsów.
- `docker-compose.yml` – orkiestruje Postgresa, Redisa, Redpandę (Kafka) i wszystkie serwisy.

## Uruchomienie lokalne
1. `cp .env.example .env` – domyślne adresy i hasła.
2. `make compose-up` – startuje gateway (`localhost:8000`), mikroserwisy (`identity:8101`, `inventory:8102`, `booking:8103`), Postgresa, Redisa, Redpandę i front (`localhost:5173`).
3. Inventory odpala Alembic na starcie, seeduje przykładowe sesje; booking publikuje zdarzenia na topic `booking.events`, inventory zmniejsza `slots_available`.
4. `make compose-down [-v]` zatrzymuje środowisko.

## Workflow dev/test
- `make lint` – Ruff.
- `make test` – wywołuje `./run-tests.sh`, który buduje kontener `tests` (Python 3.12) i uruchamia `pytest -vv`. Flagi podasz przez `make test TEST_ARGS="tests/... -k foo"`.
- Playwright e2e w `e2e/` (`npm install`, `npx playwright test`) – wymaga działającego `make compose-up` i sprawdza `/healthz`, `/auth/token`, `/events/aggregated`.

## Auth + zdarzenia
- Token demo uzyskasz z `POST /api/auth/token` (gateway deleguje do Identity) i używasz go jako `Authorization: Bearer ...` przy `/api/events/aggregated`.
- Booking → Redpanda → Inventory: zdarzenia JSON przechowywane są w logu, inventory konsumuje je i aktualizuje stan, więc serwisy nie muszą wywoływać się nawzajem HTTP.

## CI/CD
- `.github/workflows/quality.yml` – lint + pytest na push/PR.
- `.github/workflows/docker-build.yml` – buduje obrazy; ustaw `GHCR_USERNAME`/`GHCR_TOKEN` (scope `workflow`) jeśli chcesz push do `ghcr.io/<owner>/couchannel-<service>:latest`.
- `docs/DEPLOYMENT.md` – opis planu wydania (Helm/K8s, manualne aprobaty).

## Następne kroki
- Rozszerz sagę booking/płatności, dodaj analytics-service słuchający zdarzeń.
- Podłącz prawdziwego provider'a OIDC (Auth0/Keycloak) zamiast demo Identity; wdrażaj Helm chartami zgodnie z `docs/DEPLOYMENT.md`.
