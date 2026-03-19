import pandas as pd
from ingestion.utils import api_get, to_staging
from ingestion.config import LEAGUES, SEASONS

def run():
    data = api_get("fixtures", params={"league": LEAGUES, "season": SEASONS})  # [1](https://www.api-football.com/documentation-v3)
    rows = []
    for item in data.get("response", []):
        fx = item.get("fixture", {}) or {}
        lg = item.get("league", {}) or {}
        teams = item.get("teams", {}) or {}
        goals = item.get("goals", {}) or {}
        score = item.get("score", {}).get("fulltime", {}) or {}
        rows.append({
            "match_id": fx.get("id"),
            "comp_id": lg.get("id"),
            "season": lg.get("season"),
            "utc_date": fx.get("date"),
            "status": fx.get("status", {}).get("short"),
            "round": lg.get("round"),
            "home_team_id": teams.get("home", {}).get("id"),
            "away_team_id": teams.get("away", {}).get("id"),
            "ft_home_goals": score.get("home", goals.get("home")),
            "ft_away_goals": score.get("away", goals.get("away")),
            "winner": ("HOME" if teams.get("home", {}).get("winner") else
                       "AWAY" if teams.get("away", {}).get("winner") else
                       "DRAW" if score.get("home") == score.get("away") else None)
        })
    df = pd.DataFrame(rows).dropna(subset=["match_id"])
    to_staging(df, "fixtures")