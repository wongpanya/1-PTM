@echo off
setlocal
set "REPO=%~dp0.."
set "PY=C:\Users\Wongpanya.Nu\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
if not exist "%PY%" set "PY=python"

cd /d "%REPO%"

echo ==========================================
echo Phase 2 - Validate repository scaffold
echo ==========================================
echo.

echo [1/5] Git status
git status --short
if errorlevel 1 exit /b 1

echo.
echo [2/5] Latest commit
git log --oneline -1
if errorlevel 1 exit /b 1

echo.
echo [3/5] Compile Python files
"%PY%" -m compileall src scripts app.py pages
if errorlevel 1 exit /b 1

echo.
echo [4/5] Validate data
"%PY%" scripts\validate_data.py
if errorlevel 1 exit /b 1

echo.
echo [5/5] Privacy check
"%PY%" scripts\privacy_check.py
if errorlevel 1 exit /b 1

echo.
echo Phase 2 repository validation passed.
exit /b 0
