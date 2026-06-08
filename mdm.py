#!/usr/bin/env python3
# Copyright (c) 2026 Jakub Kowalski
# Licencja: MIT
import argparse
import glob
import os
import sys
from google import genai
from pydantic import BaseModel, Field

from dotenv import load_dotenv
load_dotenv()  # Automatycznie ładuje zmienne z pliku .env, jeśli ten istnieje

# 1. Definicja struktury danych za pomocą Pydantic (Structured Outputs)
class OutputFile(BaseModel):
    filename: str = Field(
        description="Dokładna nazwa lub ścieżka pliku wyjściowego, który ma zostać zaktualizowany lub utworzony."
    )
    content: str = Field(
        description="Pełna zaktualizowana lub nowo wygenerowana zawartość tego pliku wyjściowego."
    )

class ResponseModel(BaseModel):
    files: list[OutputFile] = Field(
        default=[],
        description="Lista plików wyjściowych do utworzenia lub zaktualizowania."
    )
    explanation: str | None = Field(
        default=None,
        description="Bezpośrednia odpowiedź tekstowa, komentarz lub wyjaśnienie dla użytkownika (np. w przypadku pytań lub jako uzupełnienie zmian)."
    )


def main():
    # 2. Definicja argumentów linii komend
    parser = argparse.ArgumentParser(
        description="Aktualizuje pliki wyjściowe na podstawie plików wejściowych i instrukcji za pomocą Gemini 3.5 Flash lub odpowiada na pytania."
    )
    parser.add_argument(
        "--inputs", "-i", nargs="+", required=False, default=[],
        help="Lista ścieżek do plików wejściowych (opcjonalne, obsługuje *, katalogi oraz automatyczną instrukcję na końcu)"
    )
    parser.add_argument(
        "--outputs", "-o", nargs="+", required=False, default=[],
        help="Lista ścieżek do plików wyjściowych (opcjonalne, zostaną zaktualizowane lub utworzone)"
    )
    parser.add_argument(
        "--prompt", "-p", required=False,
        default="Zaktualizuj zawartość plików wyjściowych zgodnie z komentarzami, instrukcjami TODO lub ich wewnętrznym kontekstem.",
        help="Instrukcja (prompt) opisująca zmiany lub pytanie (opcjonalna, krótka flaga: -p)"
    )

    args = parser.parse_args()

    # Sprawdzenie, czy przełącznik -p / --prompt został podany jawnie w argumentach
    has_explicit_prompt = any(arg in sys.argv for arg in ("-p", "--prompt"))

    # Jeśli nie podano przełącznika -p, a ostatni parametr skryptu nie jest istniejącym plikiem ani katalogiem, traktujemy go jako prompt
    if not has_explicit_prompt and len(sys.argv) > 1:
        last_arg = sys.argv[-1]
        if not last_arg.startswith("-") and not os.path.exists(last_arg):
            args.prompt = last_arg
            # Usuwamy go z listy, do której przypisał go argparse
            if args.inputs and args.inputs[-1] == last_arg:
                args.inputs.pop()
            elif args.outputs and args.outputs[-1] == last_arg:
                args.outputs.pop()

    # Walidacja, czy użytkownik podał cokolwiek sensownego do wykonania
    if not args.inputs and not args.outputs and args.prompt == parser.get_default("prompt"):
        print("Błąd: Musisz podać przynajmniej pliki wejściowe (-i), pliki wyjściowe (-o) lub własny prompt.", file=sys.stderr)
        sys.exit(1)

    # Rozwijanie globów (*) dla plików wejściowych
    real_inputs = []
    for pattern in args.inputs:
        matched = glob.glob(pattern, recursive=True)
        if matched:
            real_inputs.extend(matched)
        else:
            # Jeśli glob nic nie dopasował, zostawiamy oryginalny wzorzec, by wywołać ewentualny błąd braku pliku/katalogu
            real_inputs.append(pattern)

    # 3. Odczyt zawartości plików wejściowych
    inputs_content = {}
    for path in real_inputs:
        if os.path.isdir(path):
            inputs_content[path] = f"[Katalog '{path}' istnieje]"
        elif not os.path.exists(path):
            print(f"Błąd: Plik wejściowy '{path}' nie istnieje.", file=sys.stderr)
            sys.exit(1)
        else:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    inputs_content[path] = f.read()
            except Exception as e:
                print(f"Błąd podczas odczytu pliku wejściowego '{path}': {e}", file=sys.stderr)
                sys.exit(1)

    # 4. Odczyt aktualnego stanu plików wyjściowych (jeśli istnieją)
    outputs_content = {}
    for path in args.outputs:
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    outputs_content[path] = f.read()
            except Exception as e:
                print(f"Błąd podczas odczytu pliku wyjściowego '{path}': {e}", file=sys.stderr)
                sys.exit(1)
        else:
            outputs_content[path] = "[Plik jeszcze nie istnieje - utwórz go od zera]"

    # 5. Przygotowanie promptu dla modelu
    prompt_parts = []
    prompt_parts.append(
        "Jesteś asystentem programistycznym/edycyjnym. Twoim zadaniem jest zaktualizowanie plików wyjściowych "
        "na podstawie dostarczonych plików wejściowych, ich dotychczasowego stanu oraz instrukcji użytkownika. "
        "Możesz również odpowiadać na pytania użytkownika bezpośrednio, bez modyfikacji plików, jeśli taka jest intencja."
    )

    if inputs_content:
        prompt_parts.append("\n=== PLIKI WEJŚCIOWE (INPUTS) ===")
        for path, content in inputs_content.items():
            prompt_parts.append(f"Ścieżka: {path}\nZawartość:\n{content}\n" + "-" * 30)

    if outputs_content:
        prompt_parts.append("\n=== AKTUALNY STAN PLIKÓW WYJŚCIOWYCH (OUTPUTS) ===")
        for path, content in outputs_content.items():
            prompt_parts.append(f"Ścieżka: {path}\nZawartość:\n{content}\n" + "-" * 30)

    prompt_parts.append("\n=== INSTRUKCJA MODYFIKACJI LUB PYTANIE ===")
    prompt_parts.append(args.prompt)

    prompt_parts.append(
        "\nZwróć odpowiedź stosując się dokładnie do poniższego schematu JSON. "
        "Jeśli użytkownik zadał pytanie lub nie podał plików wyjściowych, umieść odpowiedź tekstową w polu 'explanation'."
    )

    prompt = "\n".join(prompt_parts)

    # 6. Inicjalizacja klienta Google GenAI (Obsługa EU / Vertex AI lub standardowego klucza API)
    vertex_project = os.environ.get("VERTEX_PROJECT")
    vertex_location = os.environ.get("VERTEX_LOCATION")  # Np. 'europe-west3' (Frankfurt) lub 'europe-west9' (Paryż)

    if vertex_project and vertex_location:
        # Konfiguracja dla Vertex AI w celu wymuszenia regionu EU
        print(f"Inicjalizacja klienta Vertex AI w regionie EU ({vertex_location})...")
        client = genai.Client(
            vertexai=True,
            project=vertex_project,
            location=vertex_location
        )
    else:
        # Standardowy dostęp przez Google AI Studio (wymaga zmiennej GEMINI_API_KEY)
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            print(
                "Błąd: Nie skonfigurowano zmiennej środowiskowej GEMINI_API_KEY.\n"
                "Możesz też użyć Vertex AI, ustawiając zmienne: VERTEX_PROJECT oraz VERTEX_LOCATION.",
                file=sys.stderr
            )
            sys.exit(1)
        client = genai.Client(api_key=api_key)

    # Użycie rekomendowanego modelu Gemini 3.5 Flash
    model_name = "gemini-3.5-flash"

    # 7. Wywołanie modelu i pobranie ustrukturyzowanej odpowiedzi
    print(f"Wysyłanie zapytania do modelu {model_name}...")
    try:
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config={ 
                "response_mime_type": "application/json",
                # Wskazujemy SDK, że chcemy otrzymać obiekt ResponseModel
                "response_schema": ResponseModel,
            },
        )
    except Exception as e:
        print(f"Błąd podczas komunikacji z API: {e}", file=sys.stderr)
        sys.exit(1)

    # 8. Parsowanie odpowiedzi i zapis na dysku
    response_data = response.parsed  # SDK automatycznie parsuje odpowiedź do obiektu Pydantic ResponseModel

    if not response_data:
        print("Błąd: Model zwrócił pustą odpowiedź lub błąd struktury danych.", file=sys.stderr)
        sys.exit(1)

    # Wyświetlenie bezpośredniej odpowiedzi / wyjaśnienia użytkownikowi
    if response_data.explanation:
        print("\n=== ODPOWIEDŹ OD MODELU ===")
        print(response_data.explanation)
        print("=" * 27)

    updated_files = response_data.files

    # Słownik pomocniczy do mapowania nazw bazowych (na wypadek, gdyby model pominął ./ w ścieżce)
    basename_map = {os.path.basename(path): path for path in args.outputs}

    if updated_files:
        print("\nAktualizacja plików na dysku:")
        for file_data in updated_files:
            target_path = None

            # Próba dopasowania dokładnej ścieżki
            if file_data.filename in args.outputs:
                target_path = file_data.filename
            else:
                # Rezerwowa próba dopasowania po samej nazwie pliku (np. "main.py" zamiast "./src/main.py")
                base = os.path.basename(file_data.filename)
                if base in basename_map:
                    target_path = basename_map[base]

            if target_path:
                try: 
                    # Upewnienie się, że katalog docelowy istnieje
                    dir_name = os.path.dirname(target_path)
                    if dir_name:
                        os.makedirs(dir_name, exist_ok=True)

                    with open(target_path, "w", encoding="utf-8") as f:
                        f.write(file_data.content)
                    print(f" [OK] Zapisano plik: {target_path}")
                except Exception as e:
                    print(f" [Błąd] Nie udało się zapisać '{target_path}': {e}", file=sys.stderr)
            else:
                print(f" [Pominięto] Model zwrócił plik '{file_data.filename}', którego nie było na liście wyjściowej.",
                      file=sys.stderr)


if __name__ == "__main__":
    main()
