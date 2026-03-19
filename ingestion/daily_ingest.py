from sqlalchemy import text
from ingestion.utils import engine
from ingestion.fetch_leagues import run as fetch_leagues
from ingestion.fetch_teams import run as fetch_teams
from ingestion.fetch_fixtures import run as fetch_fixtures
from ingestion.fetch_standings import run as fetch_standings

def main():
    # 1) extract & stage
    fetch_leagues()
    fetch_teams()
    fetch_fixtures()
    fetch_standings()

    # 2) merge to warehouse
    sql_order = [
        "db/merge_upserts.sql"  # contains the MERGE statements
    ]
    with engine().begin() as conn:
        for path in sql_order:
            with open(path, "r", encoding="utf-8") as f:
                conn.exec_driver_sql(f.read())

if __name__ == "__main__":
    main()