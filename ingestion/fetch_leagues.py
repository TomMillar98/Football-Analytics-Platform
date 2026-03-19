from ingestion.utils import api_get, to_staging
from ingestion.config import LEAGUES
import pandas as pd

def run():
    rows = []
    for league_id in LEAGUES:
        data = api_get("leagues", params={"id": league_id})

        for item in data.get("response", []):
            league = item["league"]
            country = item["country"]

            rows.append({
                "comp_id": league["id"],
                "comp_name": league["name"],
                "type": league["type"],
                "area": country["name"],
                "logo_url": league["logo"]
            })

    df = pd.DataFrame(rows)
    to_staging(df, "leagues")