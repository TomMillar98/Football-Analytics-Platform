from ingestion.utils import api_get, to_staging
from ingestion.utils import engine
from sqlalchemy import text
import pandas as pd

def run():
    rows = []

    with engine().connect() as conn:
        fixtures = conn.execute(text("SELECT fixture_id FROM staging.fixtures")).fetchall()
        fixture_ids = [f[0] for f in fixtures]

    for fixture_id in fixture_ids:
        data = api_get("fixtures/lineups", params={"fixture": fixture_id})

        for team in data.get("response", []):
            team_id = team["team"]["id"]

            for p in team["startXI"]:
                rows.append({
                    "fixture_id": fixture_id,
                    "team_id": team_id,
                    "player_id": p["player"]["id"],
                    "number": p["player"]["number"],
                    "position": p["player"]["pos"],
                    "grid": p["player"]["grid"]
                })

    df = pd.DataFrame(rows)
    to_staging(df, "player_lineups")