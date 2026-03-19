from ingestion.utils import api_get, to_staging
from ingestion.config import LEAGUES, SEASONS
import pandas as pd

def run():
    rows = []

    for league_id in LEAGUES:
        for season in SEASONS:
            data = api_get("teams", params={"league": league_id, "season": season})

            for item in data.get("response", []):
                team = item["team"]
                rows.append({
                    "team_id": team["id"],
                    "name": team["name"],
                    "short_name": team.get("code"),
                    "country": item["country"]["name"],
                    "founded": team.get("founded"),
                    "comp_id": league_id,
                    "season": season,
                    "logo_url": team["logo"]
                })

    df = pd.DataFrame(rows)
    to_staging(df, "teams")