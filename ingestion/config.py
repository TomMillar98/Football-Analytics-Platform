import os
from dotenv import load_dotenv
load_dotenv()

API_BASE = os.getenv("API_BASE", "https://v3.football.api-sports.io")
API_KEY  = os.getenv("API_FOOTBALL_KEY")  # secrets
LEAGUE_ID = int(os.getenv("LEAGUE_ID", "39"))  # Premier League by default
SEASON    = int(os.getenv("SEASON", "2024"))   # set current season

# Azure SQL connection
AZURE_SQL_CXN = os.getenv(
    "AZURE_SQL_CXN",
    "mssql+pyodbc://USERNAME:PASSWORD@YOURSERVER.database.windows.net/YOURDB"
    "?driver=ODBC+Driver+18+for+SQL+Server&Encrypt=yes&TrustServerCertificate=no"
)