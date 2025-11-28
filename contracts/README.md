# Kontrakty couchannel

Ten katalog przechowuje specyfikacje OpenAPI/AsyncAPI opisujące interfejsy usług FastAPI. Dokumenty są źródłem prawdy dla integracji i generowania SDK.

## Zawartość
- `identity.openapi.yaml` – profil użytkownika i endpointy reputacji.
- `inventory.openapi.yaml` – lista wydarzeń i dostępność miejsc.
- `booking.openapi.yaml` – tworzenie rezerwacji i statusy.

Każda zmiana interfejsu powinna aktualizować odpowiedni plik oraz przejść walidację w CI (`speccy lint` lub `openapi-cli`).
