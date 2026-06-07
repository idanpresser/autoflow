@echo off
cd /d "%~dp0"

if exist ".venv\Scripts\pythonw.exe" (
    start "" ".venv\Scripts\pythonw.exe" main.py
    exit /b 0
)

if exist ".embedded_python\pythonw.exe" (
    start "" ".embedded_python\pythonw.exe" main.py
    exit /b 0
)

echo Error: Neither virtual environment nor embedded pythonw.exe was found.
pause
exit /b 1
