from ingestion.utils import api_get, to_staging
from ingestion.config import LEAGUES, SEASONS
import pandas as pd

def run():
    rows = []

    for league_id in LEAGUES:
        for season in SEASONS:
            data = api_get("injuries", params={"league": league_id, "season": season})

            for item in data.get("response", []):
                rows.append({
                    "player_id": item["player"]["id"],
                    "team_id": item["team"]["id"],
                    "league_id": league_id,
                    "season": season,
                    "date": item["player"]["injury"]["date"],
                    "type": item["player"]["injury"]["type"],
                    "reason": item["player"]["injury"]["reason"]
                })

    df = pd.DataFrame(rows)
    to_staging(df, "player_injuries")