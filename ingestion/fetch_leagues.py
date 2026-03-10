import pandas as pd
from ingestion.utils import api_get, to_staging

def run():
    data = api_get("leagues")  # all leagues, seasons embedded  # [1](https://www.api-football.com/documentation-v3)
    rows = []
    for item in data.get("response", []):
        lg = item.get("league", {}) or {}
        area = item.get("country", {}) or {}
        rows.append({
            "comp_id": lg.get("id"),
            "comp_name": lg.get("name"),
            "comp_type": lg.get("type"),
            "area_name": area.get("name"),
            "code": lg.get("code"),
        })
    df = pd.DataFrame(rows).dropna(subset=["comp_id"])
    to_staging(df, "leagues")