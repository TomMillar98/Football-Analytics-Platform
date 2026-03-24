from ingestion.utils import engine
from sqlalchemy import text
from datetime import datetime

# modules
from ingestion.fetch_leagues import run as fetch_leagues
from ingestion.fetch_teams import run as fetch_teams
from ingestion.fetch_players import run as fetch_players
from ingestion.fetch_fixtures import run as fetch_fixtures
from ingestion.fetch_standings import run as fetch_standings
from ingestion.fetch_player_match_stats import run as fetch_player_match_stats
from ingestion.fetch_player_events import run as fetch_player_events
from ingestion.fetch_player_lineups import run as fetch_player_lineups
from ingestion.fetch_player_injuries import run as fetch_player_injuries
from ingestion.fetch_transfers import run as fetch_transfers

# upload
from ingestion.upload_images import run as upload_images


def log(msg):
    print(f"[{datetime.utcnow()}] {msg}")


def run_sql_scripts(script_paths):
    with engine().begin() as conn:
        for path in script_paths:
            log(f"Running SQL: {path}")
            with open(path, "r", encoding="utf-8") as f:
                conn.exec_driver_sql(f.read())


def main():
    start_time = datetime.utcnow()
    log("Starting Full Ingestion Pipeline")

    try:
        log("Fetching league metadata...")
        fetch_leagues()

        log("Fetching team metadata...")
        fetch_teams()

        log("Fetching players...")
        fetch_players()

        log("Fetching fixtures...")
        fetch_fixtures()

        log("Fetching standings...")
        fetch_standings()

        log("Fetching player match stats...")
        fetch_player_match_stats()

        log("Fetching player events...")
        fetch_player_events()

        log("Fetching player lineups...")
        fetch_player_lineups()

        log("Fetching player injuries...")
        fetch_player_injuries()

        log("Fetching player transfers...")
        fetch_transfers()

        # Merge
        merge_scripts = [
            "db/merge_leagues.sql",
            "db/merge_teams.sql",
            "db/merge_players.sql",
            "db/merge_fixtures.sql",
            "db/merge_standings.sql",
            "db/merge_player_match_stats.sql",
            "db/merge_player_events.sql",
            "db/merge_player_lineups.sql",
            "db/merge_injuries.sql",
            "db/merge_transfers.sql"
        ]

        run_sql_scripts(merge_scripts)

        # Was originally ingesting images but this is too much data, taking it directly from API but leaving here for future reference
        # Images
        #log("Uploading images...")
        #upload_images()

        log("Ingestion pipeline completed")

    except Exception as ex:
        log("ERROR DURING INGESTION")
        log(str(ex))
        import traceback
        traceback.print_exc()

    finally:
        end_time = datetime.utcnow()
        log(f"Total Runtime: {end_time - start_time}")


if __name__ == "__main__":
    main()