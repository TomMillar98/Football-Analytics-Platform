from __future__ import annotations
import time
from typing import Optional, Dict, Any
import pandas as pd
import requests
from sqlalchemy import create_engine
from ingestion.config import API_BASE, API_KEY, AZURE_SQL_CXN


# ============================================================
# API ERROR CLASS
# ============================================================
class ApiLimit(Exception):
    pass


# ============================================================
# HIGH‑PERFORMANCE API GET (PAID PLAN)
# ============================================================
def api_get(path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Fast GET wrapper for API-FOOTBALL v3.
    Suitable for paid plans (75k requests/day).
    Clean retry logic, no free-tier long sleeps.
    """
    url = f"{API_BASE.rstrip('/')}/{path.lstrip('/')}"
    headers = {"x-apisports-key": API_KEY}

    for attempt in range(1, 6):
        try:
            r = requests.get(url, headers=headers, params=params, timeout=20)

            # If API-Football rate-limits (rare for paid tier), retry quickly.
            if r.status_code == 429:
                sleep_s = 1 + attempt   # quick exponential backoff
                print(f"[api_get] 429 rate-limited, retrying in {sleep_s}s...")
                time.sleep(sleep_s)
                continue

            r.raise_for_status()
            return r.json()

        except requests.RequestException as e:
            if attempt == 5:
                raise
            sleep_s = 2 * attempt
            print(f"[api_get] Error {e}; retrying in {sleep_s}s (attempt {attempt}/5)")
            time.sleep(sleep_s)

    raise ApiLimit("Exceeded retries for API request")


# ============================================================
# SQL ENGINE (AZURE‑SAFE CONFIGURATION)
# ============================================================
_engine = None

def engine():
    """
    Returns a SQLAlchemy engine configured for Azure SQL.

    Key features:
    - pool_pre_ping=True  → detects dead Azure SQL TCP sessions.
    - pool_recycle=1800   → force-reconnect every 30 minutes.
    - pool_timeout=60     → allow time for reconnect.
    - fast_executemany=True → efficient bulk inserts.

    This protects the pipeline from Azure SQL timeout error 258,
    which occurs when Azure drops long-lived connections.
    """
    global _engine

    if _engine is None:
        _engine = create_engine(
            AZURE_SQL_CXN,
            pool_pre_ping=True,
            pool_recycle=1800,      # refresh connections before Azure kills them
            pool_timeout=60,
            fast_executemany=True
        )

    return _engine


# ============================================================
# STAGING WRITER (RELIABLE FOR LONG INGESTIONS)
# ============================================================
def to_staging(df: pd.DataFrame, table: str):
    """
    Writes a DataFrame into staging.<table>.
    
    Features:
    - Resets connection pool to avoid Azure idle disconnects.
    - Retries up to 5× if Azure drops connection mid-write.
    - Recreates the staging table each run (clean staging layer).
    """

    if df is None or df.empty:
        print(f"[to_staging] DataFrame for {table} is EMPTY; skipping.")
        return

    # Hard reset engine before writing (critical for >30min ingestions)
    try:
        engine().dispose()
    except Exception:
        pass

    for attempt in range(1, 6):
        try:
            with engine().begin() as conn:

                # Ensure schema exists
                conn.exec_driver_sql("""
                IF NOT EXISTS (
                    SELECT 1 FROM sys.schemas WHERE name = 'staging'
                )
                BEGIN
                    EXEC('CREATE SCHEMA staging');
                END;
                """)

                # Bulk insert
                df.to_sql(
                    name=table,
                    con=conn,
                    schema="staging",
                    if_exists="replace",
                    index=False,
                    method=None,
                    chunksize=2000
                )

                print(f"[to_staging] Wrote {len(df):,} rows to staging.{table}")
                return

        except Exception as e:
            print(f"[to_staging] SQL write failed (attempt {attempt}/5): {e}")
            time.sleep(3)

            # Reset the engine again before retrying
            try:
                engine().dispose()
            except Exception:
                pass

            if attempt == 5:
                raise