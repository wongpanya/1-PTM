from src.utils.config import load_yaml


def _is_missing(value) -> bool:
    return value is None or value == "" or str(value).lower() == "nan"


def score_row(row: dict, config_path: str = "config/risk_rules.yaml") -> dict:
    config = load_yaml(config_path)["risk_score"]
    score = 0
    components = []
    for name, rule in config["components"].items():
        triggered = _evaluate_condition(row, rule["positive_when"])
        if triggered:
            score += int(rule["weight"])
            components.append({
                "component": name,
                "score": int(rule["weight"]),
                "explanation_th": rule["explanation_th"],
            })
    return {
        "risk_score": min(score, int(config["max_score"])),
        "components": components,
    }


def _evaluate_condition(row: dict, condition: str) -> bool:
    if " is null" in condition:
        field = condition.split(" is null")[0].strip()
        return _is_missing(row.get(field))
    if " == " in condition:
        field, expected = condition.split(" == ", 1)
        field = field.strip()
        expected = expected.strip().strip('"')
        value = row.get(field)
        return str(value) == expected
    return False
