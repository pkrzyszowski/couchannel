# couchannel (PL)

couchannel to koncepcja w stylu BlaBlaCar, ale dla wspólnego oglądania sportu: gospodarze udostępniają salon + abonamenty, a goście współdzielą koszt. Repozytorium zawiera szkielet mikroserwisów (FastAPI, React, Docker Compose), który możesz uruchomić lokalnie i rozwijać według własnych pomysłów.

## Struktura
- `services/api` – FastAPI gateway/BFF z endpointami `/healthz` oraz `/events/aggregated` agregującymi dane z innych serwisów.
- `services/identity`, `services/inventory`, `services/booking`, `services/analytics` – serwisy domenowe; booking zapisuje rezerwacje + emituje zdarzenia Kafka, inventory je konsumuje, analytics agreguje statystyki ze strumienia `booking.events`.
- `apps/web` – frontend React (Vite + TS) komunikujący się z API przez `/api`.
- `contracts/` – specyfikacje OpenAPI, źródło prawdy dla interfejsów.
- `docker-compose.yml` – orkiestruje Postgresa, Redisa, Redpandę (Kafka) oraz Prometheusa/Grafanę obok serwisów.

## Uruchomienie lokalne
1. `cp .env.example .env` – domyślne adresy i hasła.
2. `make compose-up` – startuje gateway (`localhost:8000`), mikroserwisy (`identity:8101`, `inventory:8102`, `booking:8103`, `analytics:8104`), Postgresa, Redisa, Redpandę, Prometheusa (`9090`), Grafanę (`3000`) i front (`5173`).
3. Inventory odpala Alembic na starcie, seeduje przykładowe viewing sessions; booking zapisuje rezerwacje do Postgresa (`booking_records`) i publikuje zdarzenia `booking.events`, inventory zmniejsza `slots_available`, a analytics udostępnia agregaty pod `GET /stats`.
4. `make compose-down [-v]` zatrzymuje środowisko.

## Workflow dev/test
- `make lint` – Ruff.
- `make test` – wywołuje `./run-tests.sh`, który buduje kontener `tests` (Python 3.12) i uruchamia `pytest -vv`. Flagi podasz przez `make test TEST_ARGS="tests/... -k foo"`.
- Playwright e2e w `e2e/` (`npm install`, `npx playwright test`) – wymaga działającego `make compose-up` i sprawdza `/healthz`, `/auth/token`, `/events/aggregated`.

## Auth + zdarzenia
- Token demo uzyskasz z `POST /api/auth/token` (gateway deleguje do Identity) i używasz go jako `Authorization: Bearer ...` przy `/api/events/aggregated`.
- Booking → Redpanda → Inventory: zdarzenia JSON przechowywane są w logu, inventory konsumuje je i aktualizuje stan, więc serwisy nie muszą wywoływać się nawzajem HTTP.

## CI/CD
- `.github/workflows/quality.yml` – lint + pytest na PR.
- `.github/workflows/e2e.yml` – w CI uruchamia Docker Compose + Playwright (`e2e/`). Lokalnie wykonaj `cd e2e && npm install && npx playwright test` przy działającym `make compose-up`.
- Workflow budujący obrazy został przeniesiony do `.github/workflows/_unused/` i można go przywrócić, gdy pojawi się potrzeba publishowania.
- `docs/DEPLOYMENT.md` – opis planu wydania (Helm/K8s, manualne aprobaty).

## Następne kroki
- Rozszerz sagę booking/płatności, dodaj analytics-service słuchający zdarzeń.
- Podłącz prawdziwego provider'a OIDC (Auth0/Keycloak) zamiast demo Identity; wdrażaj Helm chartami zgodnie z `docs/DEPLOYMENT.md`.
