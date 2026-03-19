from ingestion.utils import api_get, to_staging
from ingestion.config import LEAGUES, SEASONS
import pandas as pd

def run():
    rows = []

    for league_id in LEAGUES:
        for season in SEASONS:
            data = api_get("standings", params={"league": league_id, "season": season})

            for item in data.get("response", []):
                standings = item["league"]["standings"][0]

                for row in standings:
                    rows.append({
                        "comp_id": league_id,
                        "season": season,
                        "team_id": row["team"]["id"],
                        "rank": row["rank"],
                        "points": row["points"],
                        "played": row["all"]["played"],
                        "won": row["all"]["win"],
                        "draw": row["all"]["draw"],
                        "lost": row["all"]["lose"],
                        "goals_for": row["all"]["goals"]["for"],
                        "goals_against": row["all"]["goals"]["against"]
                    })

    df = pd.DataFrame(rows)
    to_staging(df, "standings")