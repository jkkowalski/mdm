# Projekt TODO - Sugestie zmian i ulepszeń

Poniżej znajduje się lista sugerowanych usprawnień dla projektu `mdm`:

- [x] **Dodanie obsługi innych modeli Gemini**: Umożliwienie konfiguracji modelu Gemini (np. `gemini-2.5-pro`) za pomocą nowej flagi CLI `-m` / `--model`.
- [ ] **Obsługa zewnętrznych dostawców (Multi-provider)**: Integracja z zewnętrznymi API (np. Anthropic Claude, OpenAI GPT-5/GPT-4o) poprzez alternatywne SDK lub biblioteki uniwersalne (np. LiteLLM) w celu wsparcia modeli takich jak `claude-3-5-sonnet` lub `gpt-5.4-mini` bezpośrednio w CLI.
- [ ] **Lepsza obsługa kodowania plików**: Automatyczne wykrywanie kodowania (np. przy użyciu biblioteki `chardet` lub `charset-normalizer`) zamiast sztywnego i podatnego na błędy wymuszania `utf-8`.
- [ ] **Testy jednostkowe i integracyjne**: Dodanie katalogu `tests/` z testami w `pytest` w celu automatycznej weryfikacji poprawności działania parsera CLI, dopasowywania globów oraz samej integracji z API Google GenAI.
- [ ] **Bezpieczeństwo (try-run / preview)**: Dodanie opcji `--dry-run` lub `-d` pozwalającej na podgląd planowanych zmian przed ich faktycznym zapisaniem na dysku (np. w postaci czytelnego porównania diff w terminalu).
- [ ] **Ulepszenie interfejsu konsolowego (Rich)**: Wykorzystanie biblioteki `rich` do estetycznego wyświetlania statusów operacji, ładniejszych komunikatów błędów oraz ewentualnego paska postępu podczas komunikacji z API.
- [ ] **Ignorowanie plików (.gitignore / .mdmignore)**: Dodanie mechanizmu automatycznego ignorowania niepożądanych ścieżek (np. `.git`, `node_modules`, `__pycache__`) podczas skanowania katalogów lub rozwijania globów.
