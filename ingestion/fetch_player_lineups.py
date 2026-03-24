from ingestion.utils import api_get, to_staging, engine
from sqlalchemy import text
import pandas as pd

def run():
    rows = []

    # get fixtures already fetched
    with engine().connect() as conn:
        fixture_ids = [
            x[0] for x in conn.execute(text("SELECT fixture_id FROM staging.fixtures"))
        ]

    for fixture_id in fixture_ids:
        data = api_get("fixtures/lineups", params={"fixture": fixture_id})
        response = data.get("response", [])

        if not response:
            continue

        for team in response:
            team_id = team["team"]["id"]

            # SAFETY: handle missing or null startXI/substitute arrays
            start_xi = team.get("startXI") or []
            subs = team.get("substitutes") or []

            # starters
            for item in start_xi:
                p = item["player"]
                rows.append({
                    "fixture_id": fixture_id,
                    "team_id": team_id,
                    "player_id": p["id"],
                    "number": p.get("number"),
                    "position": p.get("pos"),
                    "grid": p.get("grid"),
                    "is_sub": 0
                })

            # substitutes
            for item in subs:
                p = item["player"]
                rows.append({
                    "fixture_id": fixture_id,
                    "team_id": team_id,
                    "player_id": p["id"],
                    "number": p.get("number"),
                    "position": p.get("pos"),
                    "grid": p.get("grid"),
                    "is_sub": 1
                })

    df = pd.DataFrame(rows)
    to_staging(df, "player_lineups")