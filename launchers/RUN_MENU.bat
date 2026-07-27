@echo off
setlocal
cd /d "%~dp0.."

:menu
cls
echo ==========================================
echo ODOS Policy Analytics Prototype Launchers
echo ==========================================
echo.
echo 0. Phase 0 - Open scope documents
echo 1. Phase 1 - Prepare and validate data
echo 2. Phase 2 - Validate repository scaffold
echo 3. Phase 3 - Run Streamlit app
echo 4. Tests  - Run tests and checks
echo 5. Git    - Show repository status
echo 9. Exit
echo.
set /p choice=Select option:

if "%choice%"=="0" call "%~dp000_phase0_open_docs.bat" & pause & goto menu
if "%choice%"=="1" call "%~dp001_phase1_prepare_data.bat" & pause & goto menu
if "%choice%"=="2" call "%~dp002_phase2_validate_repo.bat" & pause & goto menu
if "%choice%"=="3" call "%~dp003_phase3_run_app.bat" & goto menu
if "%choice%"=="4" call "%~dp004_run_tests.bat" & pause & goto menu
if "%choice%"=="5" call "%~dp005_git_status.bat" & pause & goto menu
if "%choice%"=="9" exit /b 0

echo Invalid option.
pause
goto menu
