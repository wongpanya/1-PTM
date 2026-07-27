@echo off
setlocal
set "ROOT=%~dp0..\.."
set "PY=C:\Users\Wongpanya.Nu\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"

if not exist "%PY%" set "PY=python"

echo ==========================================
echo Phase 1 - Prepare and validate data
echo ==========================================
echo.
echo This will regenerate derived Phase 1 outputs.
echo Raw Excel files will not be modified.
echo.

cd /d "%ROOT%"

"%PY%" "scripts\phase1_build_core_database.py"
if errorlevel 1 exit /b 1

"%PY%" "scripts\phase1_prepare_data_splits.py"
if errorlevel 1 exit /b 1

"%PY%" "scripts\phase1_validate_deliverables.py"
if errorlevel 1 exit /b 1

echo.
echo Phase 1 completed successfully.
exit /b 0
