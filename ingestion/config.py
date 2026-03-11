# ingestion/config.py
from __future__ import annotations

import os
from typing import List
from dotenv import load_dotenv

load_dotenv()

API_BASE = os.getenv("API_BASE", "https://v3.football.api-sports.io")
API_KEY  = os.getenv("API_FOOTBALL_KEY")  # do not hard-code this

# -------------------------------------------------------------------
# Helpers: parse comma lists and inclusive ranges (e.g., "2018-2024")
# -------------------------------------------------------------------
def _parse_csv_ints(value: str) -> List[int]:
    """
    Parse '39,78,61' -> [39, 78, 61]
    Ignores blanks and trims spaces.
    """
    out: List[int] = []
    for token in (value or "").split(","):
        token = token.strip()
        if token:
            out.append(int(token))
    return out

def _parse_range(value: str) -> List[int]:
    """
    Parse '2018-2024' -> [2018, 2019, ..., 2024]
    Also supports a single number '2024' or CSV '2018-2020,2023,2025-2026'
    """
    if not value:
        return []

    def expand_one(part: str) -> List[int]:
        part = part.strip()
        if "-" in part:
            a, b = part.split("-", 1)
            start, end = int(a), int(b)
            if end < start:
                start, end = end, start
            return list(range(start, end + 1))
        return [int(part)]

    out: List[int] = []
    for piece in value.split(","):
        out.extend(expand_one(piece))
    # de-duplicate but preserve order
    seen = set()
    deduped = []
    for n in out:
        if n not in seen:
            seen.add(n)
            deduped.append(n)
    return deduped

# -------------------------------------------------------------------
# Multi-league / multi-season environment variables
#   - LEAGUES: CSV of league IDs, e.g. "39,78,61"  (PL, Bundesliga, Ligue 1)
#   - SEASONS: year or range/CSV, e.g. "2024" or "2018-2024" or "2019,2021,2023-2024"
# Backward compatibility:
#   - If LEAGUES unset, falls back to single LEAGUE_ID (default 39).
#   - If SEASONS unset, falls back to single SEASON (default 2024).
# -------------------------------------------------------------------
_leagues_csv = os.getenv("LEAGUES", "").strip()
LEAGUES: List[int] = (
    _parse_csv_ints(_leagues_csv)
    if _leagues_csv
    else [int(os.getenv("LEAGUE_ID", "39"))]   # default Premier League
)

_seasons_expr = os.getenv("SEASONS", "").strip()
SEASONS: List[int] = (
    _parse_range(_seasons_expr)
    if _seasons_expr
    else [int(os.getenv("SEASON", "2024"))]    # default current season
)

# -------------------------------------------------------------------
# Azure SQL connection (SQLAlchemy + pyodbc)
# -------------------------------------------------------------------
AZURE_SQL_CXN = os.getenv(
    "AZURE_SQL_CXN",
    # NOTE: keep spaces URL-encoded in 'driver=' for pyodbc in SQLAlchemy URLs
    "mssql+pyodbc://USERNAME:PASSWORD@YOURSERVER.database.windows.net/YOURDB"
    "?driver=ODBC%20Driver%2018%20for%20SQL%20Server&Encrypt=yes&TrustServerCertificate=no"
)