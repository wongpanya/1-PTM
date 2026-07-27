@echo off
setlocal
set "REPO=%~dp0.."
set "PY=%REPO%\.venv\Scripts\python.exe"

cd /d "%REPO%"

if not exist "%PY%" (
  set "PY=python"
)

echo ==========================================
echo Phase 3 - Run Streamlit app
echo ==========================================
echo.

"%PY%" -c "import streamlit" >nul 2>nul
if errorlevel 1 (
  echo Streamlit is not installed in the current Python environment.
  echo.
  echo Run this first:
  echo   python -m venv .venv
  echo   .venv\Scripts\activate
  echo   pip install -r requirements.txt
  echo.
  pause
  exit /b 1
)

"%PY%" -m streamlit run app.py
exit /b %errorlevel%
