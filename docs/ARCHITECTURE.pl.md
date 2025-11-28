# Architektura mikroserwisowa couchannel

Aplikacja umożliwia gospodarzom udostępnianie miejsca i pakietów streamingowych do wspólnego oglądania wydarzeń sportowych. Kod piszemy w Pythonie 3.12 na FastAPI (serwisy + BFF), a klienci webowi/komórkowi korzystają z React/Next.js, aby projekt był łatwy do zaprezentowania rekruterom.

## Bounded Contexts i serwisy
- **Identity & Reputation** – `identity-service` (Auth0/OAuth 2.1 + WebAuthn), `trust-service` (reputacja, KYC, AML). Oddzielne magazyny: Postgres + Redis na sesje.
- **Host & Venue Management** – `hosting-service` (profil mieszkania, parametry sprzętu), `inventory-service` (kalendarz wydarzeń, liczba miejsc), `pricing-service` (dynamiczne stawki). Pliki multimedialne w S3-kompatybilnym `assets-bucket`.
- **Discovery & Engagement** – `search-service` (Elasticsearch + CQRS read models), `recommendation-service` (Kafka Streams), `notification-service` (Web Push, SMS, email), `review-service` (Event Sourcing na Postgres + Timescale).
- **Transactions** – `booking-service` jako Saga orchestrator (Temporal / Camunda), `payment-service` (Stripe/Adyen), `payout-service` (split payments), `compliance-service` (licencje i limity oglądalności), `analytics-service` (BigQuery/Snowflake).

## Wzorce projektowe
- **API Gateway + BFF** – Edge layer (Kong/Apigee) wystawia REST/gRPC, a FastAPI BFF-y (web, mobile) agregują dane dla Reacta. Umożliwia throttling, A/B, feature flags.
- **Service Discovery & Config** – Consul/Eureka + HashiCorp Vault/Dynaconf zapewniają centralne zarządzanie konfiguracją, rotację kluczy i secret zero-trust.
- **Asynchroniczna komunikacja** – Domain events na Kafka/Redpanda; w repo `booking` publikuje `booking.events`, a `inventory` konsumuje je, aktualizując dostępne miejsca. Dla synchronicznych wywołań gRPC + Circuit Breaker (Envoy + Tenacity w klientach FastAPI).
- **Federated Identity/OIDC** – `identity-service` udostępnia JWKS + endpoint wydający tokeny; gateway (FastAPI BFF) weryfikuje bearer tokeny i scope `read:events` zanim przekaże dane do frontu.
- **Saga & Choreography** – rezerwacja miejsc = `booking-service` orkiestruje `inventory`, `pricing`, `payment`, `compliance`. Przy niepowodzeniu wykonuje kompensację (odblokowanie miejsc, refund).
- **CQRS + Materialized Views** – oddzielne modele zapisu/odczytu; `search-service` buduje indeksy near-real-time z topiców `inventory.events`.
- **Observability** – OpenTelemetry, Prometheus, Tempo/Grafana. Każdy serwis ma `healthz`, `readinessz`, tracing IDs przekazywane przez gateway.
- **Resilience & Security** – Podobnie jak w BlaBlaCar: rate limiting na gateway, retry + backoff, circuit breakers, idempotentne endpointy, polityki mTLS (service mesh Istio/Linkerd) i podział tenantów.

## Przepływy krytyczne
1. Gość wyszukuje wydarzenie → API Gateway → `search-service`/`inventory` (read model) → BFF agreguje opinie + ceny.
2. Po wyborze `booking-service` rezerwuje slot (command) → publikuje `BookingInitiated`. Saga blokuje miejsca (`inventory`), kalkuluje cenę (`pricing`), autoryzuje płatność (`payment`).
3. `compliance-service` weryfikuje limity transmisji (reguły ligi, max osób). Po sukcesie `booking-service` emituje `BookingConfirmed`, a `notification-service` wysyła potwierdzenia (push/e-mail) i instrukcje do hosta.
4. Po wydarzeniu `review-service` zbiera opinie, `analytics` agreguje NPS oraz wykorzystanie pakietów streamingowych.

## Dane i magazyny
- Relacyjne dane (użytkownicy, płatności, inventory) → Postgres + Liquibase/Flyway.
- Operacje odczytu masowego → Elasticsearch, Redis, Rockset.
- Telemetria → Loki/Tempo, metadane w Mimir/Prometheus. Event log (Kafka) służy jako single source of truth dla replik.

## Stos technologiczny i Delivery
- Serwisy backend: Python 3.12 + FastAPI, Pydantic v2, SQLModel/SQLAlchemy; BFF-y także w FastAPI, a zadania asynchroniczne obsługuje Celery lub Dramatiq. gRPC/Protobuf zapewniają niskie opóźnienia między serwisami.
- Front: React 18 + Next.js (SSR/SSG) oraz aplikacja mobilna React Native; komunikacja z BFF przez GraphQL/REST; stan zarządzany przez TanStack Query / Zustand.
- Infrastrukturę pakujemy w kontenery, repo Helm chartów w `deploy/helm`, środowiska K8s (EKS/GKE). Istio zapewnia traffic shifting (canary, blue/green).
- CI/CD: GitHub Actions → `poetry run pytest`, `ruff check`, `docker build`, skanowanie Snyk/Trivy, promotion pipeline z manualnym approval.
- Local dev: `make compose-up` uruchamia kluczowe serwisy (Postgres, Redis, Kafka, Temporal) oraz routing API Gateway w trybie lightweight z Docker Compose; kontrakty dokumentowane w AsyncAPI/OpenAPI repo `contracts/`.

## Repozytorium i środowiska
- Na start pracujemy lokalnie (Docker Desktop + `docker compose up`), ale repo jest przygotowane do wypchnięcia na GitHuba; utrzymuj główne moduły w `services/<nazwa>` i front w `apps/web`/`apps/mobile`.
- Compose już zawiera podstawowe zależności (Postgres na dane trwałe, Redis na cache/session); kolejne broker'y (Kafka, Temporal) dodawaj jako osobne usługi lub profile Compose.
- Konfiguruj `.env` per serwis (trzymany lokalnie), a do commita dodawaj `.env.example`; Compose montuje tajemnice z `./deploy/local/*.env`.
- Branch main pozostaje zawsze releasowalny; feat-branch → PR → GitHub Actions → build obrazów → GitHub Container Registry.
- Po skonfigurowaniu zdalnego klastra (np. `k3d` lub `kind`) te same obrazy i Helm chart z katalogu `deploy/helm` można promować z GitHuba (manualny approval w pipeline’ach release).
