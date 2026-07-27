@echo off
setlocal
cd /d "%~dp0.."
if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" scripts\phase8_acceptance.py
) else (
  python scripts\phase8_acceptance.py
)
exit /b %errorlevel%
