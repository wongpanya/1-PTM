@echo off
setlocal
cd /d "%~dp0.."

echo ==========================================
echo Git status
echo ==========================================
echo.
git status --short
echo.
git log --oneline --decorate -5
exit /b %errorlevel%
