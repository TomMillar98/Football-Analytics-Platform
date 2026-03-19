from ingestion.utils import api_get, to_staging
import pandas as pd

def run():
    rows = []
    from ingestion.utils import engine
    from sqlalchemy import text

    # get all known players
    with engine().connect() as conn:
        p = conn.execute(text("SELECT DISTINCT player_id FROM staging.players")).fetchall()
        players = [x[0] for x in p]

    for pid in players:
        data = api_get("transfers", params={"player": pid})

        for item in data.get("response", []):
            for move in item["transfers"]:
                rows.append({
                    "player_id": pid,
                    "date": move["date"],
                    "type": move["type"],
                    "from_team": move["teams"]["in"]["name"],
                    "to_team": move["teams"]["out"]["name"]
                })

    df = pd.DataFrame(rows)
    to_staging(df, "transfers")