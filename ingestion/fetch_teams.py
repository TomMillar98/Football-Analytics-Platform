import pandas as pd
from ingestion.utils import api_get, to_staging
from ingestion.config import LEAGUE_ID, SEASON

def run():
    data = api_get("teams", params={"league": LEAGUE_ID, "season": SEASON})  # [1](https://www.api-football.com/documentation-v3)
    rows = []
    for item in data.get("response", []):
        team = item.get("team", {}) or {}
        rows.append({
            "team_id": team.get("id"),
            "team_name": team.get("name"),
            "tla": team.get("code"),
            "country": item.get("country", {}).get("name"),
            "founded": team.get("founded"),
        })
    df = pd.DataFrame(rows).dropna(subset=["team_id"])
    to_staging(df, "teams")