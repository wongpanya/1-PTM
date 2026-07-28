@echo off
setlocal
set "REPO=%~dp0.."
set "PY=%REPO%\.venv\Scripts\python.exe"
set "STREAMLIT=%REPO%\.venv\Scripts\streamlit.exe"
if not exist "%PY%" set "PY=C:\Users\Wongpanya.Nu\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
if not exist "%PY%" set "PY=python"

cd /d "%REPO%"

echo ==========================================
echo Phase 7 - External Indicators and Governance
echo ==========================================
echo.

"%PY%" scripts\run_unit_tests.py
if errorlevel 1 exit /b 1

"%PY%" scripts\privacy_check.py
if errorlevel 1 exit /b 1

if exist "%STREAMLIT%" (
  "%STREAMLIT%" run app.py
) else (
  "%PY%" -m streamlit run app.py
)
