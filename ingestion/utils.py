from __future__ import annotations
import time
from typing import Optional, Dict, Any
import pandas as pd
import requests
from sqlalchemy import create_engine, text
from ingestion.config import API_BASE, API_KEY, AZURE_SQL_CXN

# HTTP helper
class ApiLimit(Exception):
    pass


def api_get(path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    GET wrapper for API-FOOTBALL v3 with basic 429 handling.
    Uses header 'x-apisports-key'.
    """
    url = f"{API_BASE.rstrip('/')}/{path.lstrip('/')}"
    headers = {"x-apisports-key": API_KEY}

    # Basic retry/backoff on 429 or transient errors
    for attempt in range(1, 6):
        try:
            r = requests.get(url, headers=headers, params=params, timeout=30)
            if r.status_code == 429:
                # Respect ~10 req/min on free plan: small cooldown and retry
                sleep_s = min(60, 5 * attempt)
                print(f"[api_get] 429 rate-limited; sleeping {sleep_s}s (attempt {attempt}/5)")
                time.sleep(sleep_s)
                continue
            r.raise_for_status()
            return r.json()
        except requests.RequestException as e:
            if attempt == 5:
                raise
            sleep_s = min(60, 3 * attempt)
            print(f"[api_get] HTTP error: {e}; retrying in {sleep_s}s (attempt {attempt}/5)")
            time.sleep(sleep_s)

    raise ApiLimit("Exceeded retries for API request")

# SQLAlchemy engine (pyodbc) with fast_executemany
def engine():
    """
    Build an engine for Azure SQL via pyodbc.
    fast_executemany=True avoids the 2100-parameter limit problem you saw with method='multi'.
    """
    return create_engine(
        AZURE_SQL_CXN,
        pool_pre_ping=True,
        fast_executemany=True
    )

# Write a DataFrame into staging.<table> safely

def to_staging(df: pd.DataFrame, table: str):
    """
    Write DataFrame to staging.<table>, recreating the table each run.

    Why 'replace'?
      - Keeps staging a clean mirror of this run’s columns/dtypes.
      - Avoids TRUNCATE permissions and parameter-count issues.
      - Lets pandas/SQLAlchemy generate a straightforward executemany.

    NOTE: If you prefer to keep the table schema fixed, pre-create it in SQL and change
          if_exists='append' here. In that case, still keep method=None (no multi).
    """
    if df is None or df.empty:
        print(f"[to_staging] DataFrame for {table} is empty; skipping.")
        return

    with engine().begin() as conn:
        # Ensure schema exists
        conn.exec_driver_sql("""
        IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = 'staging')
        BEGIN EXEC('CREATE SCHEMA staging'); END;
        """)

        # Recreate the table (staging only), then bulk insert
        df.to_sql(
            name=table,
            con=conn,
            schema="staging",
            if_exists="replace",
            index=False,
            method=None,
            chunksize=1000
        )
        print(f"[to_staging] Wrote {len(df):,} rows to staging.{table}")