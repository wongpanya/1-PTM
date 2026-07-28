# Launchers

Windows `.bat` files in this folder are double-click launchers for common prototype tasks.

## Main Menu

From the workspace root, double-click:

```text
RUN_ODOS_MENU.bat
```

or from this repository:

```text
launchers/RUN_MENU.bat
```

## Per-Phase Buttons

- `00_phase0_open_docs.bat`: open Phase 0 scope and decision documents.
- `01_phase1_prepare_data.bat`: regenerate Phase 1 derived data and validate deliverables.
- `02_phase2_validate_repo.bat`: validate repository scaffold, data, privacy, and Python syntax.
- `003_task3_import_validate.bat`: run Task 3 import, SQLite build, validation report, and privacy check.
- `03_phase3_run_app.bat`: run the Streamlit prototype app.
- `04_phase4_data_pipeline.bat`: read raw Excel from the private Phase 1 raw copy, run cleaning, validation, quality scoring, and reports.
- `05_phase5_dashboard.bat`: refresh Phase 4 cleaned data and open the Phase 5 dashboard pages.
- `06_phase6_risk_policy.bat`: refresh cleaned data, run tests, and open the risk and policy pages.
- `07_phase7_governance.bat`: run tests and privacy checks, then open external indicators and governance pages.
- `08_phase8_acceptance.bat`: run the full automated acceptance suite and print the handover status.
- `04_run_tests.bat`: run pytest if installed, then data validation and privacy checks.
- `05_git_status.bat`: show git working tree and recent commits.
- `004_phase3_run_app.bat`, `005_run_tests.bat`, and `006_git_status.bat`: menu aliases.

## Notes

- These are Prototype launchers, not packaged production executables.
- `data/raw` must not contain committed real data.
- The app launcher requires dependencies from `requirements.txt`.
- If Streamlit is not installed yet, create a virtual environment and install requirements first.
