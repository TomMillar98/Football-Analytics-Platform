from ingestion.utils import api_get, to_staging
import pandas as pd
from ingestion.utils import engine
from sqlalchemy import text

def run():
    rows = []

    with engine().connect() as conn:
        f = conn.execute(text("SELECT fixture_id FROM staging.fixtures")).fetchall()
        fixture_ids = [x[0] for x in f]

    for fixture_id in fixture_ids:
        data = api_get("fixtures/events", params={"fixture": fixture_id})

        for e in data.get("response", []):
            rows.append({
                "fixture_id": fixture_id,
                "team_id": e["team"]["id"],
                "player_id": e["player"]["id"] if e["player"] else None,
                "type": e["type"],
                "detail": e["detail"],
                "comments": e.get("comments"),
                "minute": e["time"]["elapsed"]
            })

    df = pd.DataFrame(rows)
    to_staging(df, "player_events")