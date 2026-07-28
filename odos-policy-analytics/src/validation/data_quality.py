import pandas as pd


def completeness_table(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    total = len(df)
    for column in df.columns:
        non_missing = int(df[column].notna().sum())
        rows.append({
            "field": column,
            "non_missing": non_missing,
            "missing": total - non_missing,
            "completeness_pct": round(non_missing / total * 100, 2) if total else 0,
        })
    return pd.DataFrame(rows).sort_values("completeness_pct")
