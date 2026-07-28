from __future__ import annotations

from typing import Any

import pandas as pd

from src.utils.config import load_yaml


def agent_config() -> dict[str, Any]:
    return load_yaml("config/agents.yaml")


def agent_registry() -> pd.DataFrame:
    config = agent_config()
    rows = []
    for agent_id, item in config.get("agents", {}).items():
        rows.append(
            {
                "agent_id": agent_id,
                "agent_name": item["name"],
                "human_owner_th": item["human_owner_th"],
                "mission_th": item["mission_th"],
                "label_responsibility": item["label_responsibility"],
                "required_human_approval": item["required_human_approval"],
                "outputs": ", ".join(item.get("outputs", [])),
                "prohibited_actions": ", ".join(item.get("prohibited_actions", [])),
            }
        )
    return pd.DataFrame(rows)


def get_agent(agent_id: str) -> dict[str, Any]:
    agents = agent_config().get("agents", {})
    if agent_id not in agents:
        raise KeyError(f"Unknown agent: {agent_id}")
    return agents[agent_id]
