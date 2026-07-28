from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.agents.registry import agent_registry
from src.labeling.workflow import (
    label_definitions,
    validate_approval_register,
    validate_label_review_frame,
)
from src.utils.config import PROJECT_ROOT


def main() -> int:
    template_path = PROJECT_ROOT / "data/reference/label_review_template.csv"
    frame = pd.read_csv(template_path)
    approval_path = PROJECT_ROOT / "data/reference/label_approval_register.csv"
    approval_frame = pd.read_csv(approval_path)
    issues = [
        *validate_label_review_frame(frame),
        *validate_approval_register(approval_frame),
    ]
    definitions = label_definitions()
    agents = agent_registry()

    print(
        f"agents={len(agents)} targets={len(definitions)} "
        f"template_rows={len(frame)} approvals={len(approval_frame)}"
    )
    if issues:
        for issue in issues:
            print(f"FAIL {issue['code']}: {issue['detail']}")
        return 1
    print("Label configuration and review template passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
