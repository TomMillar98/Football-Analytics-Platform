from ingestion.utils import api_get, to_staging
from ingestion.config import LEAGUES, SEASONS
from ingestion.utils import engine
from sqlalchemy import text
import pandas as pd


def run():
    rows = []

    # Load all fixture_ids from staging
    with engine().connect() as conn:
        fixture_ids = [x[0] for x in conn.execute(
            text("SELECT fixture_id FROM staging.fixtures")
        )]

    for fixture_id in fixture_ids:
        data = api_get("fixtures/players", params={"fixture": fixture_id})
        response = data.get("response", [])

        if not response:
            continue

        for team in response:
            team_id = team["team"]["id"]

            for p in team["players"]:
                player = p["player"]
                stats_list = p.get("statistics") or []

                if not stats_list:
                    continue

                s = stats_list[0]

                rows.append({
                    "fixture_id": fixture_id,
                    "player_id": player["id"],
                    "team_id": team_id,
                    "minutes": s["games"].get("minutes"),
                    "rating": s["games"].get("rating"),
                    "shots_total": s["shots"].get("total"),
                    "shots_on": s["shots"].get("on"),
                    "passes_total": s["passes"].get("total"),
                    "passes_accuracy": s["passes"].get("accuracy"),
                    "duels_total": s["duels"].get("total"),
                    "duels_won": s["duels"].get("won"),
                    "dribbles_attempts": s["dribbles"].get("attempts"),
                    "dribbles_success": s["dribbles"].get("success"),
                    "tackles": s["tackles"].get("total"),
                    "interceptions": s["tackles"].get("interceptions"),
                    "fouls_committed": s["fouls"].get("committed"),
                    "fouls_drawn": s["fouls"].get("drawn"),
                    "saves": s["goals"].get("saves")
                })

    # Deduplicate rows before writing
    df = pd.DataFrame(rows)
    df = df.drop_duplicates(subset=["fixture_id", "player_id"])

    to_staging(df, "player_match_stats")