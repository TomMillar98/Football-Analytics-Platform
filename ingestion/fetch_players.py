from ingestion.utils import api_get, to_staging
from ingestion.config import LEAGUES, SEASONS
import pandas as pd

def run():
    rows = []

    for league in LEAGUES:
        for season in SEASONS:

            page = 1
            while True:
                data = api_get("players", params={
                    "league": league,
                    "season": season,
                    "page": page
                })

                response = data.get("response", [])
                if not response:
                    break

                for item in response:
                    p = item["player"]
                    stats = item["statistics"][0]  # always 1 element

                    rows.append({
                        "player_id":   p["id"],
                        "team_id":     stats["team"]["id"],
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
                        "position":    stats["games"]["position"],
                        "number":      stats["games"]["number"],
                        "appearances": stats["games"]["appearences"],
                        "lineups":     stats["games"]["lineups"],
                        "minutes":     stats["games"]["minutes"],
                        "goals":       stats["goals"]["total"],
                        "assists":     stats["goals"]["assists"],
                        "yellow":      stats["cards"]["yellow"],
                        "red":         stats["cards"]["red"]
                    })

                page += 1

    df = pd.DataFrame(rows)
    to_staging(df, "players")