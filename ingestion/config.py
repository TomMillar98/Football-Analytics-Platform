import os
from dotenv import load_dotenv
load_dotenv()

API_BASE = os.getenv("API_BASE", "https://v3.football.api-sports.io")
API_KEY  = os.getenv("API_FOOTBALL_KEY")


LEAGUES = [
    # England (leagues)
    39,40,41,42,
    # England (cups)
    45,48,528,

    # Spain (leagues)
    140,141,142,
    # Spain (cups)
    143,556,

    # Germany (leagues)
    78,79,80,
    # Germany (cups)
    81,529,

    # Italy (leagues)
    135,136,137,
    # Italy (cups)
    1379,1380,

    # France (leagues)
    61,62,63,
    # France (cups)
    66,528,

    # International tournaments
    1,4,5,2,3,848
]

SEASONS = [2020]

AZURE_SQL_CXN = os.getenv("AZURE_SQL_CXN")
AZURE_BLOB_CXN = os.getenv("AZURE_BLOB_CXN")