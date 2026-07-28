@echo off
setlocal
set "REPO=%~dp0.."
set "PY=%REPO%\.venv\Scripts\python.exe"
if not exist "%PY%" set "PY=C:\Users\Wongpanya.Nu\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
if not exist "%PY%" set "PY=python"

cd /d "%REPO%"

echo ==========================================
echo Phase 4 - Data Pipeline and Data Quality
echo ==========================================
echo.

"%PY%" scripts\run_phase4_pipeline.py
if errorlevel 1 exit /b 1

"%PY%" scripts\run_unit_tests.py
if errorlevel 1 exit /b 1

"%PY%" scripts\validate_data.py
if errorlevel 1 exit /b 1

"%PY%" scripts\privacy_check.py
if errorlevel 1 exit /b 1

echo.
echo Phase 4 data pipeline completed.
exit /b 0
