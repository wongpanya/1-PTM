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
echo 3. Task 3  - Import data and validate
echo 4. Phase 3 - Run Streamlit app
echo 5. Phase 4 - Run data pipeline and quality checks
echo 6. Phase 5 - Run dashboard and analytics
echo 7. Phase 6 - Run risk, forecast, and policy
echo 8. Phase 7 - Run external indicators and governance
echo 9. Tests  - Run tests and checks
echo G. Git    - Show repository status
echo X. Exit
echo.
set /p choice=Select option:

if "%choice%"=="0" call "%~dp000_phase0_open_docs.bat" & pause & goto menu
if "%choice%"=="1" call "%~dp001_phase1_prepare_data.bat" & pause & goto menu
if "%choice%"=="2" call "%~dp002_phase2_validate_repo.bat" & pause & goto menu
if "%choice%"=="3" call "%~dp003_task3_import_validate.bat" & pause & goto menu
if "%choice%"=="4" call "%~dp004_phase3_run_app.bat" & goto menu
if "%choice%"=="5" call "%~dp004_phase4_data_pipeline.bat" & pause & goto menu
if "%choice%"=="6" call "%~dp005_phase5_dashboard.bat" & goto menu
if "%choice%"=="7" call "%~dp006_phase6_risk_policy.bat" & goto menu
if "%choice%"=="8" call "%~dp007_phase7_governance.bat" & goto menu
if "%choice%"=="9" call "%~dp005_run_tests.bat" & pause & goto menu
if /i "%choice%"=="G" call "%~dp006_git_status.bat" & pause & goto menu
if /i "%choice%"=="X" exit /b 0

echo Invalid option.
pause
goto menu
