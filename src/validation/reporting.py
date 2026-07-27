from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


def write_validation_report(report: dict[str, Any], output_dir: str | Path) -> Path:
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "validation_report.json"
    md_path = out_dir / "validation_report.md"
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(_as_markdown(report), encoding="utf-8")
    return json_path


def write_issues_csv(issues: list[dict[str, Any]], output_dir: str | Path) -> Path:
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "validation_issues.csv"
    pd.DataFrame(issues).to_csv(path, index=False, encoding="utf-8-sig")
    return path


def _as_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Validation Report",
        "",
        f"- status: {report.get('status')}",
        f"- generated_at: {report.get('generated_at')}",
        f"- errors: {report.get('error_count')}",
        f"- warnings: {report.get('warning_count')}",
        "",
        "## Dataset Summary",
    ]
    for item in report.get("datasets", []):
        lines.append(f"- {item['dataset']}: {item['rows']} rows, {item['columns']} columns")
    lines.extend(["", "## Issues"])
    for issue in report.get("issues", [])[:100]:
        lines.append(f"- [{issue['severity']}] {issue['dataset']} {issue.get('field', '')}: {issue['message']}")
    if not report.get("issues"):
        lines.append("- No validation issues.")
    return "\n".join(lines)
