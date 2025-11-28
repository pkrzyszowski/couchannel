# Lokalny development couchannel

## Wymagania
- Docker Desktop lub inny zgodny runtime
- Node.js 20+ (jeśli chcesz uruchamiać web poza kontenerem)
- Python 3.12 (dla uruchomień lokalnych mikroserwisów)

## Kroki startowe
1. `cp .env.example .env` – ustaw domyślne adresy usług.
2. `make compose-up` – startuje Postgres, Redis, wszystkie mikroserwisy oraz front.
3. Front dostępny na `http://localhost:5173`, API gateway na `http://localhost:8000`.
4. Po zakończeniu: `make compose-down` (z `-v` jeśli chcesz usunąć dane Postgresa).

## Przydatne komendy
- `make lint` – uruchamia Ruff na hostcie.
- `make test` lub `./run-tests.sh` – budują kontener `tests` (python:3.12), instalują `requirements-dev.txt` i uruchamiają `pytest -vv` wewnątrz; dodatkowe flagi przekaż przez `TEST_ARGS`.
- `docker compose logs -f <service>` – tail logów konkretnej usługi.
- `docker compose exec db psql -U couchchannel -d couchchannel` – wejście do Postgresa.
- `docker compose exec inventory alembic revision --autogenerate -m "desc"` – generowanie migracji (pamiętaj o ustawionym `INVENTORY_DATABASE_URL`).

## Najczęstsze problemy
- **Inventory się nie podnosi** – sprawdź logi; jeżeli `alembic` nie ma połączenia z DB, odczekaj chwilę lub wydłuż start (np. `sleep 5 && alembic ...`).
- **Web pokazuje "Unable to reach API"** – upewnij się, że `api` działa na 8000 i pamiętaj, że proxy usuwa prefiks `/api` (konfiguracja w `apps/web/vite.config.ts`).
- **Testy nie widzą modułów** – uruchamiaj z `PYTHONPATH=$(pwd)` albo użyj wirtualnego środowiska z `pip install -r requirements-dev.txt`.
