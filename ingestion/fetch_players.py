import time
import pandas as pd
from ingestion.utils import api_get, to_staging
from ingestion.config import LEAGUES, SEASONS

def run():
    rows = []

    for league_id in LEAGUES:
        for season in SEASONS:

            page = 1
            while True:
                data = api_get("players", params={
                    "league": league_id,
                    "season": season,
                    "page": page
                })

                response = data.get("response", [])
                paging = data.get("paging", {})

                current = paging.get("current", page)
                total = paging.get("total", page)

                print(f"League {league_id}, Season {season}, Page {current}/{total}")

                if not response:
                    break

                for item in response:
                    p = item["player"]
                    s = item["statistics"][0]

                    rows.append({
                        "player_id": p["id"],
                        "team_id": s["team"]["id"],
                        "league_id": league_id,
                        "season": season,
                        "name": p["name"],
                        "firstname": p["firstname"],
                        "lastname": p["lastname"],
                        "nationality": p["nationality"],
                        "birth_date": p["birth"]["date"],
                        "height": p["height"],
                        "weight": p["weight"],
                        "injured": p["injured"],
                        "position": s["games"]["position"],
                        "number": s["games"]["number"],
                        "appearances": s["games"]["appearences"],
                        "lineups": s["games"]["lineups"],
                        "minutes": s["games"]["minutes"],
                        "goals": s["goals"]["total"],
                        "assists": s["goals"]["assists"],
                        "yellow": s["cards"]["yellow"],
                        "red": s["cards"]["red"],
                        "photo_url": p["photo"]
                    })

                if current >= total:
                    break

                page += 1
                time.sleep(0.5)

    df = pd.DataFrame(rows)
    to_staging(df, "players")