from sqlalchemy import text
from ingestion.utils import engine

from ingestion.fetch_leagues import run as fetch_leagues
from ingestion.fetch_teams import run as fetch_teams
from ingestion.fetch_fixtures import run as fetch_fixtures
from ingestion.fetch_standings import run as fetch_standings
from ingestion.fetch_players import run as fetch_players   # <-- NEW

def main():

    # ------------------------------------------------------------
    # 1) Extract → Stage
    # ------------------------------------------------------------
    print("🔄 Fetching leagues...")
    fetch_leagues()

    print("🔄 Fetching teams...")
    fetch_teams()

    print("🔄 Fetching fixtures...")
    fetch_fixtures()

    print("🔄 Fetching standings...")
    fetch_standings()

    print("🔄 Fetching players...")
    fetch_players()   # <-- NEW

    # ------------------------------------------------------------
    # 2) Load → Warehouse (MERGE)
    # ------------------------------------------------------------
    sql_scripts = [
        "db/merge_upserts.sql"      # includes merges for: competition, team, match, standing
        # If you created a new file for player merges:
        # "db/merge_players.sql"
    ]

    with engine().begin() as conn:
        for path in sql_scripts:
            print(f"📝 Running SQL merge: {path}")
            with open(path, "r", encoding="utf-8") as f:
                sql_text = f.read()
                conn.exec_driver_sql(sql_text)

    print("✅ Ingestion pipeline complete!")

if __name__ == "__main__":
    main()