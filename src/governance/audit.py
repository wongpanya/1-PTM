from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

from src.utils.config import PROJECT_ROOT


DEFAULT_AUDIT_LOG = PROJECT_ROOT / "data/processed/audit_log.jsonl"


def append_audit_event(event_type: str, payload: dict[str, Any], path: str | Path = DEFAULT_AUDIT_LOG) -> Path:
    audit_path = Path(path)
    if not audit_path.is_absolute():
        audit_path = PROJECT_ROOT / audit_path
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    event = {
        "event_type": event_type,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "payload": payload,
    }
    with audit_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")
    return audit_path
