@echo off
setlocal
set "REPO=%~dp0odos-policy-analytics"

if not exist "%REPO%\launchers\RUN_MENU.bat" (
  echo Cannot find launcher menu at "%REPO%\launchers\RUN_MENU.bat"
  echo Please confirm that Phase 2 repository exists.
  pause
  exit /b 1
)

call "%REPO%\launchers\RUN_MENU.bat"
