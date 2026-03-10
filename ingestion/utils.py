import time
import requests
import pandas as pd
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from sqlalchemy import create_engine, text
from ingestion.config import API_BASE, API_KEY, AZURE_SQL_CXN

HEADERS = {"x-apisports-key": API_KEY}  # API-FOOTBALL v3 auth header  # [1](https://www.api-football.com/documentation-v3)

class ApiLimit(Exception): ...

@retry(reraise=True,
       stop=stop_after_attempt(5),
       wait=wait_exponential(multiplier=1, min=2, max=60),
       retry=retry_if_exception_type((requests.RequestException, ApiLimit)))
def api_get(path: str, params: dict | None = None) -> dict:
    url = f"{API_BASE.rstrip('/')}/{path.lstrip('/')}"
    r = requests.get(url, headers=HEADERS, params=params, timeout=30)
    if r.status_code == 429:
        # rate-limited, respect headers if present
        time.sleep(6)  # basic cooldown for free plan (~10 req/min)  # [4](https://www.api-football.com/news/post/how-ratelimit-works)
        raise ApiLimit("Rate limited")
    r.raise_for_status()
    return r.json()

def engine():
    return create_engine(AZURE_SQL_CXN, pool_pre_ping=True)

def to_staging(df: pd.DataFrame, table: str):
    if df is None or df.empty:
        return
    with engine().begin() as conn:
        # truncate small staging table then bulk insert
        conn.execute(text(f"TRUNCATE TABLE staging.{table};"))
        df.to_sql(name=table, con=conn, schema="staging", if_exists="append", index=False, method="multi", chunksize=1000)