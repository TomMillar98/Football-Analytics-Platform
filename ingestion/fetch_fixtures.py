from ingestion.utils import api_get, to_staging
from ingestion.config import LEAGUES, SEASONS
import pandas as pd

def run():
    rows = []

    for league_id in LEAGUES:
        for season in SEASONS:
            data = api_get("fixtures", params={"league": league_id, "season": season})

            for item in data.get("response", []):
                f = item["fixture"]
                g = item["goals"]
                t = item["teams"]

                rows.append({
                    "fixture_id": f["id"],
                    "comp_id": league_id,
                    "season": season,
                    "date_utc": f["date"],
                    "status": f["status"]["long"],
                    "round": item["league"]["round"],
                    "home_team_id": t["home"]["id"],
                    "away_team_id": t["away"]["id"],
                    "referee": f.get("referee"),
                    "venue": f["venue"]["name"] if f["venue"] else None,
                    "score_home": g["home"],
                    "score_away": g["away"]
                })

    df = pd.DataFrame(rows)
    to_staging(df, "fixtures")