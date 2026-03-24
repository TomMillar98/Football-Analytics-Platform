import pandas as pd
from ingestion.utils import api_get, to_staging
from ingestion.config import LEAGUES, SEASONS


def run():
    rows = []

    for league_id in LEAGUES:
        for season in SEASONS:
            data = api_get("injuries", params={"league": league_id, "season": season})

            for item in data.get("response", []):
                inj = item.get("player", {}).get("injury", {})
                rows.append({
                    "player_id": item["player"]["id"],
                    "team_id": item["team"]["id"],
                    "league_id": league_id,
                    "season": season,
                    "date": inj.get("date"),
                    "type": inj.get("type"),
                    "reason": inj.get("reason")
                })

    df = pd.DataFrame(rows)
    to_staging(df, "player_injuries")