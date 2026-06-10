@echo off
setlocal
if exist "%~dp0venv\Scripts\python.exe" (
    "%~dp0venv\Scripts\python.exe" "%~dp0mdm.py" %*
) else if exist "%~dp0.venv\Scripts\python.exe" (
    "%~dp0.venv\Scripts\python.exe" "%~dp0mdm.py" %*
) else (
    python "%~dp0mdm.py" %*
)
endlocal