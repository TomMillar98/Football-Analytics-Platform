import time
import pandas as pd
from ingestion.utils import api_get, to_staging
from ingestion.config import LEAGUES, SEASONS

def run():
    rows = []

    for league in LEAGUES:
        for season in SEASONS:

            page = 1
            while True:
                # API CALL
                data = api_get("players", params={
                    "league": league,
                    "season": season,
                    "page": page
                })

                response = data.get("response", [])
                paging = data.get("paging", {})

                # Correct keys for API-FOOTBALL pagination
                current_page = paging.get("current", page)
                total_pages = paging.get("total", page)

                print(f"League {league}, Season {season}, Page {current_page}/{total_pages} pulled")

                # No data? Stop early
                if not response:
                    break

                # Process rows
                for item in response:
                    p = item["player"]
                    s = item["statistics"][0]

                    rows.append({
                        "player_id":   p["id"],
                        "team_id":     s["team"]["id"],
                        "league_id":   league,
                        "season":      season,
                        "name":        p["name"],
                        "firstname":   p["firstname"],
                        "lastname":    p["lastname"],
                        "nationality": p["nationality"],
                        "birth_date":  p["birth"]["date"],
                        "height":      p["height"],
                        "weight":      p["weight"],
                        "injured":     p["injured"],
                        "position":    s["games"]["position"],
                        "number":      s["games"]["number"],
                        "appearances": s["games"]["appearences"],
                        "lineups":     s["games"]["lineups"],
                        "minutes":     s["games"]["minutes"],
                        "goals":       s["goals"]["total"],
                        "assists":     s["goals"]["assists"],
                        "yellow":      s["cards"]["yellow"],
                        "red":         s["cards"]["red"]
                    })

                # Stop if this was the last page
                if current_page >= total_pages:
                    break

                # NEXT PAGE
                page += 1

                # IMPORTANT: protect free‑tier API limit (10 req/min)
                time.sleep(21)

    df = pd.DataFrame(rows)
    to_staging(df, "players")