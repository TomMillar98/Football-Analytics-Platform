from ingestion.utils import api_get, to_staging
from ingestion.config import LEAGUES, SEASONS
import pandas as pd

def run():
    rows = []

    # Pulling all fixtures
    from sqlalchemy import text
    from ingestion.utils import engine
    with engine().connect() as conn:
        fixtures = conn.execute(text("SELECT fixture_id FROM staging.fixtures")).fetchall()
        fixture_ids = [f[0] for f in fixtures]

    for fixture_id in fixture_ids:
        data = api_get("fixtures/players", params={"fixture": fixture_id})

        for item in data.get("response", []):
            team = item["team"]["id"]

            for p in item["players"]:
                s = p["statistics"][0]

                rows.append({
                    "fixture_id": fixture_id,
                    "player_id": p["player"]["id"],
                    "team_id": team,
                    "minutes": s["games"]["minutes"],
                    "rating": s["games"]["rating"],
                    "shots_total": s["shots"]["total"],
                    "shots_on": s["shots"]["on"],
                    "passes_total": s["passes"]["total"],
                    "passes_accuracy": s["passes"]["accuracy"],
                    "duels_total": s["duels"]["total"],
                    "duels_won": s["duels"]["won"],
                    "dribbles_attempts": s["dribbles"]["attempts"],
                    "dribbles_success": s["dribbles"]["success"],
                    "tackles": s["tackles"]["total"],
                    "interceptions": s["tackles"]["interceptions"],
                    "fouls_committed": s["fouls"]["committed"],
                    "fouls_drawn": s["fouls"]["drawn"],
                    "saves": s["goals"]["saves"]
                })

    df = pd.DataFrame(rows)
    to_staging(df, "player_match_stats")