@echo off
setlocal enabledelayedexpansion

echo ==================================================
echo Rozpoczynanie instalacji i konfiguracji srodowiska
echo ==================================================

:: 1. Tworzenie wirtualnego srodowiska
echo [1/3] Tworzenie wirtualnego srodowiska venv...
if not exist "%~dp0venv" (
    python -m venv venv
    if !ERRORLEVEL! neq 0 (
        echo [BLAD] Nie udalo sie utworzyc wirtualnego srodowiska. Upewnij sie, ze Python jest zainstalowany i dodany do zmiennej PATH.
        goto :error
    )
    echo Wirtualne srodowisko zostalo utworzone pomyślnie.
) else (
    echo Srodowisko venv juz istnieje.
)

:: 2. Instalacja bibliotek z requirements.txt
echo [2/3] Instalacja zaleznosci z pliku requirements.txt...
if exist "%~dp0requirements.txt" (
    call "%~dp0venv\Scripts\activate.bat"
    python -m pip install --upgrade pip
    pip install -r "%~dp0requirements.txt"
    if !ERRORLEVEL! neq 0 (
        echo [BLAD] Wystapil blad podczas instalacji zaleznosci.
        call deactivate
        goto :error
    )
    call deactivate
    echo Biblioteki zostaly pomyślnie zainstalowane.
) else (
    echo [OSTRZEZENIE] Nie znaleziono pliku requirements.txt. Pomijanie instalacji pakietow.
)

:: 3. Dodawanie sciezki do PATH uzytkownika
echo [3/3] Dodawanie biezacego katalogu do zmiennej PATH uzytkownika...
set "CURRENT_DIR=%~dp0"
:: Usuniecie ewentualnego ukosnika na koncu sciezki
if "%CURRENT_DIR:~-1%"=="\" set "CURRENT_DIR=%CURRENT_DIR:~0,-1%"

:: Pobranie aktualnego PATH uzytkownika z rejestru (bezpieczniejsze niz setx %PATH% ze wzgledu na limit znakow)
set "USER_PATH="
for /f "tokens=2*" %%A in ('reg query HKCU\Environment /v PATH 2^>nul') do (
    set "USER_PATH=%%B"
)

:: Sprawdzenie czy sciezka juz istnieje w PATH
if not "!USER_PATH!"=="" (
    echo "!USER_PATH!" | findstr /I /C:";%CURRENT_DIR%;" >nul
    if !ERRORLEVEL! equ 0 (
        set "ALREADY_EXISTS=1"
    ) else (
        echo "!USER_PATH!" | findstr /I /C:";%CURRENT_DIR%" >nul
        if !ERRORLEVEL! equ 0 (
            set "ALREADY_EXISTS=1"
        ) else (
            echo "!USER_PATH!" | findstr /I /C:"%CURRENT_DIR%;" >nul
            if !ERRORLEVEL! equ 0 (
                set "ALREADY_EXISTS=1"
            ) else (
                set "ALREADY_EXISTS=0"
            )
        )
    )
) else (
    set "ALREADY_EXISTS=0"
)

if "!ALREADY_EXISTS!"=="1" (
    echo Katalog docelowy jest juz w zmiennej PATH.
) else (
    if not "!USER_PATH!"=="" (
        setx PATH "!USER_PATH!;%CURRENT_DIR%"
    ) else (
        setx PATH "%CURRENT_DIR%"
    )
    echo Ppomyslnie dodano "%CURRENT_DIR%" do PATH uzytkownika!
    echo UWAGA: Aby zmiany w PATH weszly w zycie, musisz uruchomic ponownie terminal/konsole.
)

echo ==================================================
echo Instalacja zakonczona sukcesem!
echo ==================================================
pause
exit /b 0

:error
echo ==================================================
echo [BLAD] Instalacja przerwana z powodu bledow.
echo ==================================================
pause
exit /b 1
