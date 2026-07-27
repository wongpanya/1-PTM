@echo off
setlocal
set "REPO=%~dp0.."
set "PY=%REPO%\.venv\Scripts\python.exe"
if not exist "%PY%" set "PY=C:\Users\Wongpanya.Nu\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
if not exist "%PY%" set "PY=python"

cd /d "%REPO%"

echo ==========================================
echo Task 3 - Import data and validate
echo ==========================================
echo.

"%PY%" scripts\import_data.py
if errorlevel 1 exit /b 1

"%PY%" scripts\build_database.py
if errorlevel 1 exit /b 1

"%PY%" scripts\validate_data.py
if errorlevel 1 exit /b 1

"%PY%" scripts\privacy_check.py
if errorlevel 1 exit /b 1

echo.
echo Task 3 import and validation completed.
exit /b 0
