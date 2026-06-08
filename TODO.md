# Projekt TODO - Sugestie zmian i ulepszeń

Poniżej znajduje się lista sugerowanych usprawnień dla projektu `mdm`:

- [ ] **Dodanie obsługi innych modeli LLM**: Umożliwienie łatwej konfiguracji modelu (np. `gemini-2.5-pro` lub `claude-3-5-sonnet`) za pomocą nowej flagi CLI lub odpowiednich zmiennych w pliku `.env`.
- [ ] **Lepsza obsługa kodowania plików**: Automatyczne wykrywanie kodowania (np. przy użyciu biblioteki `chardet` lub `charset-normalizer`) zamiast sztywnego i podatnego na błędy wymuszania `utf-8`.
- [ ] **Testy jednostkowe i integracyjne**: Dodanie katalogu `tests/` z testami w `pytest` w celu automatycznej weryfikacji poprawności działania parsera CLI, dopasowywania globów oraz samej integracji z API Google GenAI.
- [ ] **Bezpieczeństwo (try-run / preview)**: Dodanie opcji `--dry-run` lub `-d` pozwalającej na podgląd planowanych zmian przed ich faktycznym zapisaniem na dysku (np. w postaci czytelnego porównania diff w terminalu).
- [ ] **Ulepszenie interfejsu konsolowego (Rich)**: Wykorzystanie biblioteki `rich` do estetycznego wyświetlania statusów operacji, ładniejszych komunikatów błędów oraz ewentualnego paska postępu podczas komunikacji z API.
- [ ] **Ignorowanie plików (.gitignore / .mdmignore)**: Dodanie mechanizmu automatycznego ignorowania niepożądanych ścieżek (np. `.git`, `node_modules`, `__pycache__`) podczas skanowania katalogów lub rozwijania globów.
t 