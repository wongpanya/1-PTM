@echo off
setlocal
set "ROOT=%~dp0..\.."
set "REPO=%~dp0.."

echo Opening Phase 0 and scope documents...
echo.
echo Main scope:
echo %ROOT%\PROJECT_SCOPE.md
echo.
echo Phase 0 docs:
echo %ROOT%\docs\phase0\PROJECT_CHARTER.md
echo %ROOT%\docs\phase0\ACCEPTANCE_CHECKLIST.md
echo %ROOT%\docs\phase0\DECISION_LOG.md
echo.

start "" "%ROOT%\PROJECT_SCOPE.md"
if exist "%ROOT%\docs\phase0\PROJECT_CHARTER.md" start "" "%ROOT%\docs\phase0\PROJECT_CHARTER.md"
if exist "%ROOT%\docs\phase0\ACCEPTANCE_CHECKLIST.md" start "" "%ROOT%\docs\phase0\ACCEPTANCE_CHECKLIST.md"
if exist "%ROOT%\docs\phase0\DECISION_LOG.md" start "" "%ROOT%\docs\phase0\DECISION_LOG.md"

exit /b 0
