import pandas as pd
from ingestion.utils import api_get, to_staging
from ingestion.config import LEAGUE_ID, SEASON

def run():
    data = api_get("standings", params={"league": LEAGUE_ID, "season": SEASON})  # [1](https://www.api-football.com/documentation-v3)
    rows = []
    for item in data.get("response", []):
        comp_id = item["league"]["id"]
        season = item["league"]["season"]
        for table in item["league"]["standings"]:
            for row in table:
                team = row["team"]
                rows.append({
                    "comp_id": comp_id,
                    "season": season,
                    "team_id": team["id"],
                    "position": row["rank"],
                    "points": row["points"],
                    "played": row["all"]["played"],
                    "won": row["all"]["win"],
                    "draw": row["all"]["draw"],
                    "lost": row["all"]["lose"],
                    "goals_for": row["all"]["goals"]["for"],
                    "goals_against": row["all"]["goals"]["against"],
                })
    df = pd.DataFrame(rows)
    to_staging(df, "standings")