# mdm.py - AI-powered File Editor & Generator

Narzędzie konsolowe w języku Python wykorzystujące model **Gemini** (domyślnie `gemini-3.5-flash`) do inteligentnego aktualizowania lub tworzenia plików wyjściowych na podstawie dostarczonych plików wejściowych, ich dotychczasowej zawartości oraz instrukcji użytkownika.

## Spis treści
- [Opis projektu](#opis-projektu)
- [Wymagania systemowe i zależności](#wymagania-systemowe-i-zależności)
- [Instalacja i konfiguracja](#instalacja-i-konfiguracja)
- [Uruchamianie globalne (Windows)](#uruchamianie-globalne-windows)
- [Sposób użycia](#sposób-użycia)
- [Zaawansowane funkcje CLI](#zaawansowane-funkcje-cli)
- [Jak to działa](#jak-to-działa)
- [Przykłady](#przykłady)
- [Licencja](#licencja)

## Opis projektu
Skrypt `mdm.py` umożliwia zautomatyzowaną modyfikację kodu źródłowego, dokumentacji oraz innych plików tekstowych przy użyciu sztucznej inteligencji. Przekazuje on do modelu LLM kontekst w postaci plików wejściowych, aktualnego stanu plików wyjściowych oraz precyzyjnych wskazówek, a następnie automatycznie zapisuje wygenerowane i ustrukturyzowane zmiany bezpośrednio na dysku.

## Wymagania systemowe i zależności
* Python w wersji 3.10 lub nowszej
* Aktywne konto i klucz API w usłudze **Google AI Studio** lub projekt w **Google Cloud (Vertex AI)**
* Wymagane biblioteki Python:
  * `google-genai` (nowy, oficjalny klient Google GenAI)
  * `pydantic` (do walidacji i strukturyzowania danych wyjściowych)
  * `python-dotenv` (do automatycznego ładowania zmiennych środowiskowych z pliku `.env`)

## Instalacja i konfiguracja

1. Zainstaluj wymagane zależności przy użyciu `pip`:
   ```bash
   pip install google-genai pydantic python-dotenv
   ```

2. Skonfiguruj zmienne środowiskowe. Możesz to zrobić, tworząc plik `.env` w katalogu ze skryptem:

   **Opcja A: Korzystanie z Google AI Studio (rekomendowane)**
   ```env
   GEMINI_API_KEY=twój_klucz_api_gemini
   ```

   **Opcja B: Korzystanie z Vertex AI (Google Cloud, wymuszenie regionu EU)**
   ```env
   VERTEX_PROJECT=nazwa_twojego_projektu_gcp
   VERTEX_LOCATION=europe-west3
   ```

## Uruchamianie globalne (Windows)

Aby móc wygodnie korzystać z narzędzia `mdm` z dowolnego miejsca w systemie Windows:
1. Dodaj folder zawierający pliki `mdm.py` oraz `mdm.bat` do systemowej zmiennej środowiskowej **PATH**.
2. Od tego momentu możesz wywoływać narzędzie bezpośrednio komendą `mdm` zamiast `python mdm.py`:
   ```cmd
   mdm -i plik.txt -o wynik.txt "zmień tekst"
   ```

## Sposób użycia

Uruchom skrypt z poziomu terminala, przekazując ścieżki do plików wejściowych, wyjściowych oraz treść instrukcji (promptu):

```bash
python mdm.py -i <pliki_wejściowe...> -o <pliki_wyjściowe...> -p "<instrukcja>"
```

Każdy z kluczowych parametrów posiada intuicyjny skrót odpowiadający pierwszej literze jego nazwy:

### Argumenty:
* `--inputs`, `-i` (opcjonalne) - Lista ścieżek do plików wejściowych, które stanowią kontekst/źródło danych dla modelu. Obsługuje dzikie karty `*` (globbing) oraz ścieżki do katalogów.
* `--outputs`, `-o` (opcjonalne) - Lista ścieżek do plików wyjściowych, które mają zostać zmodyfikowane lub utworzone od zera. Jeśli parametr nie zostanie podany, narzędzie może służyć do zadawania pytań (odpowiedź generowana jest jako wyjaśnienie bez zapisu na dysku).
* `--prompt`, `-p` (opcjonalne) - Instrukcja tekstowa opisująca zmiany, jakie model ma wprowadzić, lub bezpośrednie pytanie.
* `--model`, `-m` (opcjonalne, domyślnie: `gemini-3.5-flash`) - Wybór modelu LLM z rodziny Gemini (np. `gemini-3.5-flash`, `gemini-2.5-pro`). Ponieważ skrypt korzysta z oficjalnego Google GenAI SDK, obsługa modeli innych dostawców (takich jak OpenAI GPT czy Anthropic Claude) nie jest bezpośrednio wbudowana w silnik API.

## Zaawansowane funkcje CLI

1. **Obsługa wieloznaczników `*` (globbing):**
   Możesz przekazać wzorce plików do parametru `-i`, na przykład `-i src/*.py`, co automatycznie załaduje wszystkie pasujące pliki.

2. **Obsługa katalogów:**
   Jeśli przekażesz ścieżkę do katalogu w parametrze `-i`, skrypt prześle do modelu bezpieczną informację o istnieniu tego katalogu (np. `[Katalog 'src/' istnieje]`), bez próby wczytywania go jako pliku tekstowego.

3. **Uproszczone podawanie instrukcji (bez `-p`):**
   Jeśli nie podasz przełącznika `-p` ani `--prompt`, a ostatni parametr przekazany do skryptu nie jest istniejącym plikiem ani katalogiem na dysku, zostanie on **automatycznie zinterpretowany jako instrukcja (prompt)**. Zostanie on wtedy usunięty z listy plików (wejściowych lub wyjściowych, w zależności od tego, gdzie został zaklasyfikowany przez interpreter linii komend). Dzięki temu możesz pisać krótsze komendy, np.:
   ```bash
   mdm -i src/*.py -o src/*.py "Dodaj brakujące docstringi"
   ```

## Jak to działa
1. Skrypt odczytuje zawartość wszystkich wskazanych plików wejściowych (obsługując katalogi i dopasowania typu globbing).
2. Wyodrębnia instrukcję końcową z ostatniego argumentu linii poleceń, jeśli nie została podana z użyciem `-p`.
3. Odczytuje obecny stan plików wyjściowych (jeżeli nie istnieją, przekazuje informację o konieczności ich utworzenia od zera).
4. Buduje szczegółowy prompt zawierający zebrany kontekst oraz instrukcję modyfikacji.
5. Wysyła zapytanie do wybranego modelu (np. `gemini-3.5-flash` lub `gemini-2.5-pro`) przy użyciu mechanizmu **Structured Outputs** (gwarantującego poprawność zwracanego formatu JSON zgodnego ze schematem Pydantic).
6. Analizuje odpowiedź, wyświetla ewentualne wyjaśnienie i bezpiecznie zapisuje zaktualizowane pliki na dysku (tworząc w razie potrzeby brakujące katalogi nadrzędne).

## Przykłady

Wybór bardziej zaawansowanego modelu do skomplikowanej refaktoryzacji:
```bash
python mdm.py -i src/*.py -o src/*.py -m gemini-2.5-pro "Przeprowadź głęboką analizę logiczną i popraw błędy współbieżności"
```

Aktualizacja dokumentacji na podstawie kodu źródłowego przy użyciu wildcards:
```bash
python mdm.py -i src/*.py -o README.md -p "przygotuj plik README na podstawie tych plików"
```

Szybkie wywołanie bez użycia flagi `-p`:
```bash
python mdm.py -i logic.py -o test_logic.py "Napisz testy jednostkowe w pytest"
```

Zadanie pytania dotyczącego analizy kodu (bez modyfikacji plików wyjściowych):
```bash
python mdm.py -i mdm.py "Jak działa obsługa argumentów bez flagi -p?"
```

Generowanie testów jednostkowych dla całego katalogu:
```bash
python mdm.py -i src/*.py -o tests/test_all.py "Stwórz szkielet testów dla plików w tym katalogu"
```

## Licencja
Projekt udostępniany na licencji MIT. Autor: Jakub Kowalski (2026). Szczegóły znajdują się w pliku `LICENSE`.
